---
layout: post_page
title: Writing Trading Utilities in JavaScript - part 1
excerpt: In this blog post, I will show JavaScript code for utilities which should be helpful to programmers who work on professional financial trading systems (including HFT or high frequency trading and algorithmic trading)
comments: true
---
<link href="//maxcdn.bootstrapcdn.com/font-awesome/4.2.0/css/font-awesome.min.css" rel="stylesheet">

In this blog post I will show how to write utilities for financial trading software using JavaScript. Specifically, I will write a very simple implementation of FIX protocol, a TCP protocol used widely across the trading industry. The code I show here will be useful for writing higher level support and monitoring tools but won't be fast enough to be used in latency sensitive environments.

As with my previous posts, my goal is to investigate concepts and technologies I don't get to use very much at work. Hopefully fellow trading system developers will save a few hours or a few days of work. Those of you who are not trading system developers should enjoy a peek into a new industry.

### Utilities, not trading systems
Let me limit the scope of problems I am attempting to tackle in this post. Most professional trading systems are written in C++, Java and C#. Many latency sensitive (aka HFT or High Frequency Trading) companies are even moving to hardware only solutions. It clearly doesn't make sense to try to shoehorn JavaScript in such environments. The code presented here should be used to build non-latency sensitive tools.

If book on Amazon are an indication, "trading system" often means strategies used by day traders. in this post, I use the term to mean professional trading systems. Almost all of my experience is with the kinds of trading environments one might see at hedge funds or brokers. I don't have any experience working with individual traders, aka day traders.

Finally, I hope readers understand the code shown here, written over a few nights, shouldn't be used to trade actual money. Monitor your trades, calculate P&L, measure ack times, sure. Don't trade money (your own or your clients').

### FIX protocol
In trading environments, much of what developers do involves streaming data such as prices of assets and order status updates such as fills, cancels, rejections and the like. An earlier [post] (http://falconair.github.io/2015/01/05/financial-exchange.html) of mine describes financial exchanges from a developer's perspective and may be informative to you. Another earlier [post](http://targetcompid.tumblr.com/post/39879066034/what-is-fix-protocol) describes the FIX protocol in greater detail, although I will go over the basics here again.

FIX or Financial Exchange Protocol is a text based TCP/IP protocol which has been in use for over 25 years<sup>[1](#footnote1)</sup>. It is a set of set of tag, value pairs separated by a delimiter (actual delimiter is the non-printable character SOH, not ';' as shown below).

<br>

### <span style="color: #993300;">8</span><span style="color: #999999;">=</span>FIX.4.2<span style="color: #999999;">;</span><span style="color: #993300;">9</span><span style="color: #999999;">=</span>035<span style="color: #999999;">;<span style="color: #993300;">49</span>=<span style="color: #000000;">SENDERID</span>;<span style="color: #993300;">52</span>=<span style="color: #000000;">TARGETID</span>;....;</span><span style="color: #993300;">10</span><span style="color: #999999;">=</span>345<span style="color: #999999;">;</span>
<br>

Messages start with tag 8, containing the version of FIX, followed by tag 9, containing the length of the message and end with tag 10, which contains a checksum, used to confirm the integrity of the message. Every FIX message also contains other administrative fields, such as the time a message was sent, sequence numbers to make sure gaps are identified, identification tokens of the sender and receiver and the type of message being transmitted. The remaining tags contain business specific information. For example, if the message contains a new order, it will contain symbol, quantity, price and other related information. FIX defines a fairly large number of message types, although just a handful are used by most companies. Our examples will look at Login, Login response, NewOrderSingle (new orders) and ExecutionReport (acknowledgement of receipt, fill notification, etc.).

I'm always impressed by colleagues who can read these messages as if they were English prose. I'm not one of those people, which is why I created [this](http://fixparser.targetcompid.com) tool. Paste your FIX messages in there and it will parse them and show you the result in an easy to interpret table. Thousands of people find it useful so don't feel bad if you don't like the idea of memorizing the tags.

This post is mainly concerned with parsing standard FIX messages<sup>[2](#footnote2)</sup> to build higher level utilities. Professional trading system developers will already know what I'm describing here and newbies only need an overview so I won't go into further details about FIX message hierarchy.

### User level API
FIX is a low level wire protocol, which means a developer writing utilities or tools should be provided with a higher level interface. I chose to use JavaScript's new Map interface. A map contains keys and values, which maps cleanly<sup>[3](#footnote3)</sup> to FIX's tags and values. For example, a user should be able to code like this: ```message.set('symbol','GOOG')```, rather than doing text munging.

_<span class="fa fa-warning " aria-hidden="true" style="display:inline-block;"></span> A note about JavaScript Map, I'm not sure I will continue to use it. I feel like Map and the object literal syntax cover the same territory for me. Why would I move away from built-in JSON syntax to using a Map? I'm sure professional JavaScript developers have good reasons but I just ended up with a sub-optimal API._

#### Utility lookup dictonaries
Recall that FIX is structured as tag=value;tag=value... where tags are all numeric. In code examples, I am using the API as if the tags were string mnemonics. I am able to do this because I make use of _fields_ and _msgs_ dictionaries I show below. Otherwise I would have to remember (or lookup each time) the correct tag number. In the code below, you will often see `fields['<string mnemonic>']` which returns the numeric tag for the mnemonic from a dictionary. Incidentally, the dictionaries also contain numeric tag to string mnemonic mappings, so `fields['35']` will return 'MsgType.' There are similar mappings for message types and enums for fields. The data for these dictionaries comes from QuickFIXEngine's [website](http://quickfixengine.org/). I believe they generated this data from more complex data files provided by the folks who manage FIX. In the repository for this [blog](https://github.com/falconair/TradingToolsInNode), I provide xsl style sheets which convert this data to JSON files.

A peek inside the _fields_ dictionary:

###### <span style="color: #999999;">{</span> ...

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">1</span><span style="color: #999999;">':'</span>Account<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">Account</span><span style="color: #999999;">':'</span>1<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">2</span><span style="color: #999999;">':'</span>AdvId<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">AdvId</span><span style="color: #999999;">':'</span>2<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">3</span><span style="color: #999999;">':'</span>AdvRefID<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">AdvRefID</span><span style="color: #999999;">':'</span>3<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">4</span><span style="color: #999999;">':'</span>AdvSide<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">AdvSide</span><span style="color: #999999;">':'</span>4<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">5</span><span style="color: #999999;">':'</span>AdvTransType<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">AdvTransType</span><span style="color: #999999;">':'</span>5<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">6</span><span style="color: #999999;">':'</span>AvgPx<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">AvgPx</span><span style="color: #999999;">':'</span>6<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">7</span><span style="color: #999999;">':'</span>BeginSeqNo<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">BeginSeqNo</span><span style="color: #999999;">':'</span>7<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">8</span><span style="color: #999999;">':'</span>BeginString<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">BeginString</span><span style="color: #999999;">':'</span>8<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">9</span><span style="color: #999999;">':'</span>BodyLength<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">BodyLength</span><span style="color: #999999;">':'</span>9<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">10</span><span style="color: #999999;">':'</span>Checksum<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">Checksum</span><span style="color: #999999;">':'</span>10<span style="color: #999999;">',</span>

###### ... <span style="color: #999999;">}</span>
<br>
Complete contents of _msgs_ dictionary (for FIX version 4.0):

###### <span style="color: #999999;">{</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">7</span><span style="color: #999999;">':'</span>Advertisement<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">Advertisement</span><span style="color: #999999;">':'</span>7<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">P</span><span style="color: #999999;">':'</span>AllocationInstructionAck<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">AllocationInstructionAck</span><span style="color: #999999;">':'</span>P<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">J</span><span style="color: #999999;">':'</span>Allocation<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">Allocation</span><span style="color: #999999;">':'</span>J<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">Q</span><span style="color: #999999;">':'</span>DontKnowTrade<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">DontKnowTrade</span><span style="color: #999999;">':'</span><span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">C</span><span style="color: #999999;">':'</span>Email<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">Email</span><span style="color: #999999;">':'</span>5<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">8</span><span style="color: #999999;">':'</span>ExecutionReport<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">ExecutionReport</span><span style="color: #999999;">':'</span>8<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">0</span><span style="color: #999999;">':'</span>Heartbeat<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">Heartbeat</span><span style="color: #999999;">':'</span>0<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">6</span><span style="color: #999999;">':'</span>IOI<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">IOI</span><span style="color: #999999;">':'</span>6<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">K</span><span style="color: #999999;">':'</span>ListCancelRequest<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">ListCancelRequest</span><span style="color: #999999;">':'</span>K<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">L</span><span style="color: #999999;">':'</span>ListExecute<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">ListExecute</span><span style="color: #999999;">':'</span>L<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">N</span><span style="color: #999999;">':'</span>ListStatus<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">ListStatus</span><span style="color: #999999;">':'</span>N<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">M</span><span style="color: #999999;">':'</span>ListStatusRequest<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">ListStatusRequest</span><span style="color: #999999;">':'</span>M<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">A</span><span style="color: #999999;">':'</span>Logon<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">Logon</span><span style="color: #999999;">':'</span>5<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">5</span><span style="color: #999999;">':'</span>Logout<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">Logout</span><span style="color: #999999;">':'</span>5<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">E</span><span style="color: #999999;">':'</span>NewOrderList<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">NewOrderList</span><span style="color: #999999;">':'</span>E<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">D</span><span style="color: #999999;">':'</span>NewOrderSingle<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">NewOrderSingle</span><span style="color: #999999;">':'</span>D<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">B</span><span style="color: #999999;">':'</span>News<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">News</span><span style="color: #999999;">':'</span>B<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">9</span><span style="color: #999999;">':'</span>OrderCancelReject<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">OrderCancelReject</span><span style="color: #999999;">':'</span>9<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">G</span><span style="color: #999999;">':'</span>OrderCancelReplaceRequest<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">OrderCancelReplaceRequest</span><span style="color: #999999;">':'</span>G<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">F</span><span style="color: #999999;">':'</span>OrderCancelRequest<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">OrderCancelRequest</span><span style="color: #999999;">':'</span>F<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">H</span><span style="color: #999999;">':'</span>OrderStatusRequest<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">OrderStatusRequest</span><span style="color: #999999;">':'</span>H<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">S</span><span style="color: #999999;">':'</span>Quote<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">Quote</span><span style="color: #999999;">':'</span>S<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">3</span><span style="color: #999999;">':'</span>Reject<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">Reject</span><span style="color: #999999;">':'</span>3<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">2</span><span style="color: #999999;">':'</span>ResendRequest<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">ResendRequest</span><span style="color: #999999;">':'</span>2<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">4</span><span style="color: #999999;">':'</span>SequenceReset<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">SequenceReset</span><span style="color: #999999;">':'</span>4<span style="color: #999999;">',</span>

###### &nbsp; <span style="color: #999999;">'</span><span style="color: #993300;">1</span><span style="color: #999999;">':'</span>TestRequest<span style="color: #999999;">',</span> <span style="color: #999999;">'</span><span style="color: #993300;">TestRequest</span><span style="color: #999999;">':'</span>1<span style="color: #999999;">',</span>

######  <span style="color: #999999;">}</span>

There are, naturally, many different types of messages communicated over FIX. Each of those messages has a number of fields. The first JSON snippet shows mappings to/from numeric tags from/to mnemonics. The second code block shows message type mappings between numeric tags and mnemonics.


_<span class="fa fa-warning" aria-hidden="true" style="display:inline-block;"></span> QuickFIXEngine and QuickFIX/J are a pair of FIX implementations which have existed since the dawn of time and provide very stable code. Many companies use their code in production. My code here should be thought of as a bunch of utilities for writing FIX code, their code is a much more complete solution, which naturally adds a bit more complexity._

Keep in mind that in some cases, using these dictionaries can become quite complex. For example, if you want to create a transaction where the ExecTransType field is set to NEW, you need two lookups, one for the field and another for the enum value related to that field. This code look like this: `enums[fields['ExecTransType']]['NEW']`. Add to it the logic to set a key in a map and that single line of code looks like this:

```javascript
fill.set(fields['ExecTransType'], enums[fields['ExecTransType']]['NEW']);
```

The screenshot below shows how code differs when you make use of the lookup dictionaries provided. On one hand, it does increase the size of code a bit, but, to my eyes at least, the added characters contain far more signal than noise. If you and your colleagues have all the tag memorized, keep the code simple and ignore the lookup dictionaires.

<div style="margin: 0 auto;width: 100%;">
<img src="/assets/trading-tools-in-javascript/diff.png" width="100%">
</div>
> ###### Difference when using message, field and enum mnemonic helpers (screenshot from github)

#### Map interface
Creating a new message means creating a map, populating it with values and having a utility function convert it to text which can be published to the network. If you want to buy 100 shares of Google, you add to the map 'GOOG' as the symbol, 100 as quantity and perhaps some price as the limit. All messages contain session specific sequence numbers, sender and target IDs, timestamps, etc. It makes no sense for you to provide these manually. This is why the FIXSession object manages these values for session. You can choose to send a bad sequence number, if you want to test such behavior, but the default is to fill in as much information for you as is reasonable.

#### Hearetbeat management
Similarly, managing heartbeat messages is a pain, which is why the Heartbeater object handles these for you<sup>[4](#footnote4)</sup> (as long as you enable them).

Create FIXSession and Heartbeater as follows:

```javascript
const fix_session = new FIXSession( "FIX.4.2", 'SENDERID', 'TARGETID');
const heartbeater = new Heartbeater(fix_session);
...
heartbeater.enable(<seconds between heartbeats>);
```

_<span class="fa fa-warning" aria-hidden="true" style="display:inline-block;"></span> A note about JavaScript streams interface. I had a difficult time correctly using streams and while the current implementation has been tested, I still may not fully understand it. A large part of the confusion was that I kept expecting them to work like Netty's [ChannelPipeline](https://netty.io/4.0/api/io/netty/channel/ChannelPipeline.html), which uses the Intercepting [Filter pattern](https://en.wikipedia.org/wiki/Intercepting_filter_pattern). Sometime around 2011 I had my own [implementation](https://github.com/falconair/nodepipe) of this pattern in npm under the name 'pipe' (although another coder asked to take over the name). In the code I show below, you will often see that I am writing data as `heartbeater.write(..)` instead of `socket.write(...).` This is because `heartbeater` is piped with the transport socket as `heartbeater.pipe(socket)`_

`heartbeater` just listens for outgoing messages and if a message hasn't been sent in predefined number of seconds, it sends a heartbeat. This logic is annoying enough that it is coded in its own class which is added to your code via a pipe, most users don't have to deal with it.


### TCP server and client in node
Before I go any further, here is what a simple client looks like in node (adapted from Node's docs):

```javascript
const net = require('net');
const client = net.connect({port: 8124}, () => {
  console.log('connected to server!');
  client.write('world!\r\n');
});
client.on('data', (data) => {
  console.log(data.toString());
  client.end();
});
```

The server implementation is even simpler:

```javascript
const net = require('net');
const server = net.createServer((c) => {
  console.log('client connected');
  c.on('end', () => { console.log('client disconnected'); });
  c.on('data', () => { console.log('client data:'+data); });
  c.write('hello\r\n');
}).listen(8124, () => { console.log('server bound'); });
```


### Raw string to higher level data structures, and back

#### RegexFrameDecoder: Convert TCP stream to whole messages
TCP doesn't know where one message ends and another begins. If you get a notification of a new message, it may be half a message or five and a half messages. This means that we need to extract full messages off the network buffer and leave incomplete messages in there for later processing. Some [earlier](https://github.com/falconair/nodefix) [projects](https://github.com/falconair/fix.js) of mine provide a more complete implementation of FIX use a much more efficient and logically correct frame decoding<sup>[6](#footnote1)</sup> logic. For the purpose of this post, I just use a simple regex to look for the beginning and the end of a message. This is what you see in the `RegexFrameDecoder` class below:

```javascript
class RegexFrameDecoder extends stream.Transform{
  constructor(regex,opt){
    super(opt);
    this.buffer = '';
    this.regex = regex;
  }

  _transform(chunk, encoding, callback){
    const chunks = (this.buffer + chunk).toString().split(this.regex);
    for(var i = 0; i < chunks.length -1; i++){ this.push(chunks[i]); }
    this.buffer = chunks[chunks.length-1];
    callback();
  }
}
```
_<span class="fa fa-warning" aria-hidden="true" style="display:inline-block;"></span> As I mentioned a moment ago, this code doesn't take performance into account at all. I'm also probably misusing .toString() here instead of correctly setting the encoding for streams._


I add this decoder to the input socket stream, so by the time users see data, they see fully formed, individual messages:

```javascript
socket
  .pipe(new RegexFrameDecoder(/(8=.+?\x0110=\d\d\d\x01)/g))
  .on('data', (data)=>{
    const fix = data.toString();
    ...
  });
```

#### toMap: convert message strings to Map data structure
Code to convert this message to a map is trivial, and is included in the FIXSession class as a utility method:

```javascript
static toMap(fix){
  const arr = fix.split(/\x01/g).map((e)=>{return e.split('=')});
  return new Map(arr);
}
```

Visually, this line:
<span style="color: #993300;">8</span><span style="color: #999999;">=</span>FIX.4.2<span style="color: #999999;">;</span><span style="color: #993300;">9</span><span style="color: #999999;">=</span>035<span style="color: #999999;">;<span style="color: #993300;">49</span>=<span style="color: #000000;">SENDERID</span>;<span style="color: #993300;">52</span>=<span style="color: #000000;">TARGETID</span>;....;</span><span style="color: #993300;">10</span><span style="color: #999999;">=</span>345<span style="color: #999999;">;</span>

is converted to this:
<span style="color: #999999;">{</span><span style="color: #999999;">'</span><span style="color: #993300;">8</span><span style="color: #999999;">':'</span>FIX.4.2<span style="color: #999999;">',</span><span style="color: #999999;">'</span><span style="color: #993300;">9</span><span style="color: #999999;">':'</span>035<span style="color: #999999;">',</span><span style="color: #999999;">'</span><span style="color: #993300;">49</span><span style="color: #999999;">':'</span>SENDERID<span style="color: #999999;">',</span><span style="color: #999999;">'</span><span style="color: #993300;">52</span><span style="color: #999999;">':'</span>TARGETID<span style="color: #999999;">',</span><span style="color: #999999;">'</span><span style="color: #993300;">10</span><span style="color: #999999;">':'</span>345<span style="color: #999999;">',</span><span style="color: #999999;">...</span><span style="color: #999999;">}</span>


#### toFIXString: convert messages in Map datastructure back to string
Code to convert a map to a string which can be sent over the wire is not as simple:

```javascript
toFIXString(fixmap,calcFields={'bodylength':true, 'checksum':true, 'msgseqnum':true, 'sendingtime':true}){
  const SOH = '\x01';

  let tag8  = fixmap.get('8')  || false; fixmap.delete('8');//BeginString
  let tag9  = fixmap.get('9')  || false; fixmap.delete('9');//length
  let tag35 = fixmap.get('35') || false; fixmap.delete('35');//MsgType
  let tag10 = fixmap.get('10') || false; fixmap.delete('10');//checksum
  let tag34 = fixmap.get('34') || false; fixmap.delete('34');//MsgSeqNum
  let tag52 = fixmap.get('52') || false; fixmap.delete('52');//SendingTime

  let fixarr = Array.from(fixmap);
  let body_no_seqnum_sendtime = fixarr.map((e)=>{return e.join(':')}).join(SOH);

  let seqnum_sendtime = [];

  if(calcFields['sendingtime']) seqnum_sendtime.push('52='+FIXSession._getUTCTimeStamp());
  else if(tag52) seqnum_sendtime.push('52='+tag52);

  if(calcFields['msgseqnum']) seqnum_sendtime.push('34='+this.seqnum_counter.next());
  else if(tag34) seqnum_sendtime.push('34='+tag34);

  const body = ['35='+ tag35, seqnum_sendtime.join(SOH) , body_no_seqnum_sendtime,''].join(SOH);

  let header = []

  if(tag8) header.push('8='+tag8);

  if(calcFields['bodylength']) header.push('9='+(body.length ));
  else if(tag9) header.push('9='+tag9);

  const headbody = [header.join(SOH) , body].join(SOH);

  let tail = [];

  if(calcFields['checksum']) tail.push('10='+FIXSession._checksum(headbody));
  else if(tag10) tail.push('10='+tag10);

  const headbodytail = [headbody , tail.join(SOH),SOH].join('');

  return headbodytail;
}

```
The code above takes in a map containing user fields, strips out fields which need to be calculated, such as checksum, length, timestamp, etc. Calculates the required fields and adds them back in. User can choose to provide their own values for calculated fields (for example, if you want to send the wrong sequence number on purpose to test some functionality). This function interface has gone through a few versions and it still doens't feel optimal.

#### _checksum: a utility memthod to calculate and format checksum
Checksum calculation logic is also annoying and is provided here:

```javascript
static _checksum(fix){
  var chksm = 0;
  for (var i = 0; i < fix.length; i++) { chksm += fix.charCodeAt(i);}

  chksm = chksm % 256;

  var checksumstr = '';
  if (chksm < 10) {
    checksumstr = '00' + (chksm + '');
  } else if (chksm >= 10 && chksm < 100) {
    checksumstr = '0' + (chksm + '');
  } else {
    checksumstr = '' + (chksm + '');
  }

  return checksumstr;
}
```

The code above calculates the checksum and returns the output in three digits. There are a few other functions, such as UTC time formatter which are not included since they are not very interesting.

### Sample client
I've shown the most important parts of the code. Let's combine all the coponents studied above and write a simple FIX client which connects to an exchange or a broker and sends a logon message:

```javascript
//includes elided
const fix_session = new FIXSession( "FIX.4.2", 'SENDER', 'TARGET');
const heartbeater = new Heartbeater(fix_session);


const socket = new net.Socket();
socket.setEncoding('ascii');

heartbeater
  .pipe(new stream.Transform({transform(chunk,e,cb){console.log("OUTGOING:"+chunk.toString());cb(null,chunk);}}))
  .pipe(socket);

socket
  .pipe(new RegexFrameDecoder(/(8=.+?\x0110=\d\d\d\x01)/g))
  .pipe(new stream.Transform({transform(chunk,e,cb){console.log("INCOMING:"+chunk.toString());cb(null,chunk);}}))
  .on('data', (data)=>{
    const fix = data.toString();
    const fixmap = FIXSession.toMap(fix);

    if(FIXSession.isMsgType(fixmap, msgs["Logon"])){
      //kick off heartbeats
      heartbeater.enable(fixmap.get(fields['HeartBtInt']));
    }
  });

socket.on('close', ()=>{
  console.log('Disconnected');
  heartbeater.disable();
});

socket.connect(9878, 'localhost', ()=>{
  console.log('Connected');
  //Send logon
  const logon_ = fix_session.create_msg(msgs['Logon'], {[fields['HeartBtInt']]:'10', [fields['EncryptMethod']]:'0'});
  logon_.set(fields['HeartBtInt'], '10');
  heartbeater.write(fix_session.toFIXString(logon_));
});
```
The code above creates a FIXSession object, a heart beat manager, streams which extract individual messages, adds logging to incoming and outgoing messages, sends a logon and extracts heart beat time from the logon response.

### Sample server (with order execution logic)
I tested the server code shown below by launching QuickFix/J's order sender. Part of the test included sending an order from the GUI and expecting an acknowledgement and an execution. The following code shows how this is done:

```javascript
//includes elided
const server = net.createServer((socket) => {
  socket.setEncoding('ascii')
  let fix_session = null;
  let heartbeater = null;


  console.log(`${socket.remoteAddress} connected`);

  socket
    .pipe(new RegexFrameDecoder(/(8=.+?\x0110=\d\d\d\x01)/g))
    .pipe(new stream.Transform({transform(chunk,e,cb){console.log("INCOMING:"+chunk.toString());cb(null,chunk);}}))
    .on('data', (data)=>{
      const fix = data.toString();
      const fixmap = FIXSession.toMap(fix);

      if(FIXSession.isMsgType(fixmap, msgs["Logon"])){
        //create session with correct compids
        fix_session = new FIXSession("FIX.4.2", fixmap.get(fields['TargetCompID']), fixmap.get(fields['SenderCompID']));
        heartbeater = new Heartbeater(fix_session);
        heartbeater
        .pipe(new stream.Transform({transform(chunk,e,cb){console.log("OUTGOING:"+chunk.toString());cb(null,chunk);}}))
        .pipe(socket);

        //kick off heartbeats
        const heartbtint = fixmap.get(fields['HeartBtInt']);
        heartbeater.enable(heartbtint);

        //respond to logon
        const logon_ = fix_session.create_msg(msgs['Logon'], {[fields['HeartBtInt']]:heartbtint, [fields['EncryptMethod']]:'0'});
        heartbeater.write(fix_session.toFIXString(logon_));
      }

      if(FIXSession.isMsgType(fixmap, msgs["NewOrderSingle"])){
        //ack the order
        const orderid = fix_session.orderid_counter.next();

        const ack = fix_session.create_msg(msgs['ExecutionReport']);
        ack.set(fields['ExecID'],fix_session.execid_counter.next());
        ack.set(fields['OrderID'],orderid);
        ack.set(fields['ClOrdID'],fixmap.get(fields['ClOrdID']));
        ack.set(fields['ExecType'], enums[fields['ExecType']]['NEW']);
        ack.set(fields['ExecTransType'], enums[fields['ExecTransType']]['NEW']);
        ack.set(fields['OrdStatus'], enums[fields['OrdStatus']]['NEW']);
        ack.set(fields['Side'], fixmap.get(fields['Side']));
        ack.set(fields['Symbol'], fixmap.get(fields['Symbol']));
        ack.set(fields['LeavesQty'], fixmap.get(fields['OrderQty']));
        ack.set(fields['CumQty'], '0');
        ack.set(fields['AvgPx'], '10');//execute everything at $10

        heartbeater.write(fix_session.toFIXString(ack));

        //just fill everything
        const fill = fix_session.create_msg(msgs['ExecutionReport']);
        fill.set(fields['ExecID'],fix_session.execid_counter.next());
        fill.set(fields['OrderID'],orderid);
        fill.set(fields['ClOrdID'],fixmap.get(fields['ClOrdID']));
        fill.set(fields['ExecType'], enums[fields['ExecType']]['FILL']);
        fill.set(fields['ExecTransType'], enums[fields['ExecTransType']]['NEW']);
        fill.set(fields['OrdStatus'], enums[fields['OrdStatus']]['FILLED']);
        fill.set(fields['Side'], fixmap.get(fields['Side']));
        fill.set(fields['Symbol'], fixmap.get(fields['Symbol']));
        fill.set(fields['LeavesQty'], '0');
        fill.set(fields['CumQty'], fixmap.get(fields['OrderQty']));
        fill.set(fields['AvgPx'], '10');//execute everything at $10

        heartbeater.write(fix_session.toFIXString(fill));
      }

  });

  socket.on('close', ()=>{
    console.log(`${socket.remoteAddress} disconnected`)
    heartbeater.disable();
  });


}).listen(9878,() => {
  console.log('opened server on', server.address());
});
```

The most interesting part of that code is how the acknowledgement and fill messages are created. At this point many of you should be crying out for an API, perhaps a DSL, which hides away all this detail. Unfortunately that remains to be done, perhaps for a future post or client work<sup>[5](#footnote5)</sup>.

<div style="margin: 0 auto;width: 100%;">
<img src="/assets/trading-tools-in-javascript/sequencediagram.png" width="100%">
</div>
> ###### An overview of how various snippets of code interact


### How to use this code
Near the end of the last section, you were seeing lots of code. Keep in mind that the whole implementation, the common code, the test client, the test server, the frame decoder, the heart beat manager and all the code I didn't include in this post adds up to less than 400 lines. Sure, there are many features I didn't include[1,2,3,4] but this is still enough to be useful.

Given this base, one can build many productivity enhancing tools such as:

* ###### A dummy exchange for testing a trading system
With just a few lines, you can build an order executor based on your own rules. Do you just want to execute everything? Use the code I already provided (or use QuickFIX's executor). Want to reject some percentage of order or leave them hanging without any acknowledgement? Just change a few lines.  Want to test some upcoming functionality such as yet another variation of the uptick rule, code it up in quickly and easily and test your systems.
* ###### A proxy or a router
Route your orders through a proxy to test message enrichment or perhaps to concurrently test old and new versions of your software.
* ###### A GUI for interactive FIX message creation, etc.
You can use the code provided here to generate any type of order (or a large number of them). However, non-technical users don't want to work with code. Wrap a GUI around this code and make life easier for support or QA folks.
* ###### Real-time FIX monitor
Here is a preview of of an upcoming change to [http://fixparser.targetcompid.com](http://fixparser.targetcompid.com) which will take real-time messages being published to it (instead of just pasting in batch messages). Use node's pipe mechanism to intercept incoming and outgoing messages and send them over a websocket :

<div style="margin: 0 auto;width: 75%;">
<img src="/assets/trading-tools-in-javascript/streamingfixparser.gif" width="100%">
</div>
> ###### An upcoming version of FIX parser showing real-time updates!

* ###### Real-time positions or open orders monitor
The following screen capture shows a GUI for monitoring positions and open shares. The logic behind these features is around 70 lines of code.

<div style="margin: 0 auto;width: 50%;">
<img src="/assets/trading-tools-in-javascript/streamingpositions.gif" width="100%">
</div>
> ###### Notice that positions and open shares are being updated in real-time (it can handle any number of symbols)


### Why JavaScript?
Trading industry generally employs programmers who work on server side code. There is (relatively) little front-end development, and even server frameworks such as servlets, J2EE or other web related frameworks are not part of main trading engine code. I've often worked on projects where there was not even a connection to any relational database (no JDBC or ODBC), no connection to any nosql and certainly no ORM.

In this environment, it is easy for trading software developers to be ignorant of the rich (and often overwhelming) ecosystems around ruby, python or JavaScript. JavaScript is particularly interesting because no matter what you think of the language, it's interpreter is part of every single browser. JavaScript works in many environments, from multi-GPU behemoths to tiny call phones (possibly even watches). You can open the [dev toolbox](https://developer.chrome.com/devtools) of whatever browser you are using and have instant access to an interactive environment where you can type code and evaluate it. What's more, the interpreters are pretty good and only getting better!

The language itself has started evolving faster and when there are gaps in features or libraries, users fill them quickly. Websockets are trivial to use in node but frustratingly unfriendly in Java. JSON seems to have replaced XML as structured format of choice is trivial to use in JavaScript (it essentially _is_ a subset of JS). JavaScript's ecosystem is dynamic, exciting and absurd. If ["Software is eating the world"](http://a16z.com/2016/08/20/why-software-is-eating-the-world/) then JavaScript, will surely start eating software written in other languages.

Web graphics can already be [rendered](http://www.creativebloq.com/3d/30-amazing-examples-webgl-action-6142954) by the GPU, how long until a tensforflow like framework [exists](http://cs.stanford.edu/people/karpathy/convnetjs/) for JavaScript? Jupyter notebook is spreading like wildfire among those at the intersection of science and computation, but why would we continue to tolerate requiring a python back-end (and a server on which to run it) when a much more interactive notebook could exist wholly in the [browser](https://medium.com/@mbostock/a-better-way-to-code-2b1d2876a3a0)? When developing a graphical interface for some business app, it is silly to ignore web based technologies (either web apps or [desktop](https://electron.atom.io/) solutions using web tech).

JavaScript is famous for its [warts](https://i.redd.it/h7nt4keyd7oy.jpg) but the ecosystem around it is so rich that productivity is much higher. The next time you are writing a tool where low latency is not a requirement, take a serious look at JavaScript.


<a name="footnote1">1</a>: Some colleagues think that FIX is nearing the end of its life. I disagree.

<a name="footnote2">2</a>: I only cover FIX 4.0 to 4.4.

<a name="footnote3">3</a>: Not so clean actually, I ignore repeating groups.

<a name="footnote4">4</a>: The code presented here doesn't check for _incoming_ heartbeats

<a name="footnote5">5</a>: Send contracts my way

<a name="footnote5">6</a>: The "frame decoder" terminology comes from the Netty project. I'm not sure if this is a standard term.
