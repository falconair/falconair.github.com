---
layout: post_page
title: Java APIs for socket programming
---

As of JDK 7, Java has three separate APIs for network programming. Most programmers don't write such low level code. Even those of us who write financial trading systems use higher level code. Market data vendors such as Bloomberg, Reuters and Activ provide their own libraries. Connections to other brokers or market centers are over their proprietary libraries or, more likely, over FIX protocol. Messaging queues, such as JMS and its various implementation in the Java world, are far more convenient than working directly with sockets. There are times however, when knowledge of socket level programming comes in handy. Java gives three main methods of doing socket programming, and several options within those methods. The following is my attempt to exercise each socket I/O API and learn what it offers.

### Test Setup
The code for these tests is written to be as small as possible. I try to separate message parsing code from connection handling code. Each client connects to the server, one at a time, and receives a large number of messages containing two values: server time stamp and message counter.  The client parses these messages, compares server time stamp to local time stamp to calculate latency and compares counter value to make sure no messages were dropped. At the end of the run, client also records the total time it took to transfer all messages.  Note that this is a client oriented test. I attempt to measure throughput and latency, but NOT scalability. In other words, I want to know which client handles the most number of messages per second or throughout. Since my background is in trading systems, I care _even more_ about which client is able to receive a message quickest or latency. The number of connection a server can handle, or scalability, is a very important performance measure for servers, just not for this test.

####Server
<pre><code class="language-java">
//Very simple server which handles only one client at a time and simply sends them two 'long' values in a tight loop.
...
final ServerSocket server = new ServerSocket(PORT);
while(true){
    final Socket c1 = server.accept();
    c1.setTcpNoDelay(true);
    long counter = 0;
    DataOutputStream serverout;
    try {
        serverout = new DataOutputStream(c1.getOutputStream());
        for(int i=0;i < SENDCOUNT;i++){
            serverout.writeLong(System.nanoTime());
            serverout.writeLong(counter);
            counter++;
        }
    } catch (IOException e) { e.printStackTrace(); }
    finally{ try { c1.close(); } catch (IOException e) { e.printStackTrace();} }
}
</code></pre>

###Java Streams (Old IO)
The first set of tests use the oldest socket API in java. This also happens to be the easiest to use.  These clients use the InputStream interface, sometimes by itself, sometimes wrapping BufferedInputStream and/or DataInputStreams around it. Buffer size is not applicable for Input or DataInput streams and is ignored.

####Parser Code
<pre><code class="language-java">
//Parser code for InputStream and BufferedInputStream
...
private final byte[] internalBufferBA = new byte[8];
...
public void process(InputStream input) throws IOException{
    while(true){
        size = input.read(internalBufferBA, 0, 8);
        if(size == -1) break;
        long remoteTS = toLong(internalBufferBA);

        size = input.read(internalBufferBA, 0, 8);
        if(size == -1) break;
        long remoteCounter = toLong(internalBufferBA);
        ...
    }
}
</code></pre>

<pre><code class="language-java">
//Parser code for DataInputStream
...
public void process(DataInputStream input) throws IOException{
    ...
    while(true){
        long remoteTS = input.readLong();
        long remoteCounter = input.readLong();
        ...
    }
    ...
</code></pre>

####Connection Code
<pre><code class="language-java">
//Connection code for InputStream, BufferedInputStream, DataInputStream and Buffered DataInputStream
...
Socket client = new Socket(InetAddress.getLocalHost(), PORT);
client.setTcpNoDelay(TCP_NO_DELAY);

//InputStream, BufferedInputStream, DataInputStream and Buffered DataInputStream share exactly the same code, except the next line
InputStream in = client.getInputStream();
//InputStream in = new BufferedInputStream(client.getInputStream(), bufferSize);
//DataInputStream in = new DataInputStream(client.getInputStream());
//DataInputStream in = new BufferedInputStream(new DataInputStream(client.getInputStream()), bufferSize);

try{
    p.startTimer();
    p.process(in);
    p.endTimer();
}
finally{ client.close(); }
</code></pre>


###New IO (NIO)

The second set of tests use the Channel interface provided by the NIO library. Channels may be used in a blocking manner, but they are supposed to be used in conjunction with a selector. User programs register their interest in connection, read or write events and are notified accordingly. One of the clients uses neither selectors nor blocking. This client simply spins in an empty loop until data is available to consume. The implementation and the results are interesting.

####Parser Code (shared by all NIO and NIO2 clients)
<pre><code class="language-java">
...
private final ByteBuffer internalBufferBB = ByteBuffer.allocate(8);
...
public void process(int size, ByteBuffer buf){
    //if buffer is big enough to contain both vlaues, get them and process them
    //else do ByteBuffer management, see full source code for full implementation
    ...
    if(internalBufferBB.position() == 8 && buf.remaining() >= 8){
        internalBufferBB.flip();
        remoteTS = internalBufferBB.getLong();
        internalBufferBB.clear();
        remoteCounter = buf.getLong();
    }
    ...
}
</code></pre>

####Connection Code
<pre><code class="language-java">
//NIO channels in blocking mode
..
SocketChannel channel = SocketChannel.open();
channel.setOption(StandardSocketOptions.TCP_NODELAY,TCP_NO_DELAY);
channel.connect(new InetSocketAddress(InetAddress.getLocalHost(), PORT));

ByteBuffer data = ByteBuffer.allocate(bufferSize);
int size = 0;
try{
    ...
    while(-1 != (size = channel.read(data))){
        data.flip();
        p.process(size, data);
        data.clear();
    }
    ...
}
finally{ channel.close();}
...
</code></pre>

<pre><code class="language-java">
//NIO channels in non-blocking mode, using empty spin to poll for data
...
SocketChannel channel = SocketChannel.open();
channel.setOption(StandardSocketOptions.TCP_NODELAY,TCP_NO_DELAY);
channel.configureBlocking(false);
channel.connect(new InetSocketAddress(InetAddress.getLocalHost(), PORT));
channel.finishConnect();

ByteBuffer data = ByteBuffer.allocate(bufferSize);
int size = 0;
try{
    ...
    while(-1 != (size = channel.read(data))){
        if(size != 0){
            data.flip();
            p.process(size, data);
            data.clear();
        }
    }
    ...
}
finally{ channel.close();}
...
</code></pre>


<pre><code class="language-java">
//NIO channels in non-blocking mode, using Selectors
...
Selector selector = Selector.open();

SocketChannel channel = SocketChannel.open();
channel.setOption(StandardSocketOptions.TCP_NODELAY,TCP_NO_DELAY);
channel.configureBlocking(false);
channel.register(selector, SelectionKey.OP_READ);
channel.connect(new InetSocketAddress(InetAddress.getLocalHost(), PORT));

ByteBuffer data = ByteBuffer.allocate(bufferSize);
int size = 0;
channel.finishConnect();
...
try{
    while(true){

        selector.select();

        Iterator< SelectionKey> iter = selector.selectedKeys().iterator();
        while(iter.hasNext()){
            SelectionKey key = iter.next();
            iter.remove();
            //remove selectionKey, since we are going to deal with it now
            if(key.isReadable()){
                size = ((SocketChannel)key.channel()).read(data);
                if(size != -1){
                    data.flip();
                    p.process(size, data);
                    data.clear();
                }
                else{
                    ...
                }
            }
        }
    }
}
catch(Exception e){ e.printStackTrace();}
finally{ channel.close();}
...
</code></pre>




###New IO 2 (NIO.2)
The last set of tests uses Java's latest I/O API, called NIO2. This API is truly asynchronous. A word of caution, asynchronous style of programming is not natural to Java programmers so design and test you programs well (node.js dabblers will confirm callback spaghetti code). Also pay attention to use of anonymous inner class and recursive method. I suspect this style of programming will become more prevalent when lambda functions arrive in JDK 8.

<pre><code class="language-java">
//NIO2 Async client
final AsynchronousSocketChannel channel = AsynchronousSocketChannel.open();
channel.setOption(StandardSocketOptions.TCP_NODELAY,TCP_NO_DELAY);
Future< Void> connectFuture = channel.connect(new InetSocketAddress(InetAddress.getLocalHost(), PORT));
connectFuture.get();

final ByteBuffer data = ByteBuffer.allocate(bufferSize);
try{
    ...
    channel.read(data, null, new CompletionHandler< Integer, Void>() {

        @Override public void completed(Integer result, Void att) {
            final int size = result.intValue();

            if(size != -1){
                data.flip();
                p.process(size, data);
                data.clear();
                channel.read(data,null,this);
            }
            else{
                ...
                latch.countDown();
            }
        }

        @Override public void failed(Throwable exc, Void att) { exc.printStackTrace();}
    });

    latch.await();
}
finally{ channel.close();}
</code></pre>

<!--script src="/js/nv.d3.min.js"></script-->
<script src="javaioresult.js"></script>
