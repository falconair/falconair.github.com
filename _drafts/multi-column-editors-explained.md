---
layout: post_page
title: Multi-column editors, explained
excerpt: We need editors for high resolution monitors
comments: true
---
A few weeks ago I wrote a quick little [note] (http://falconair.github.io/2015/03/03/we-need-multicolumn-editors.html) on the need for multi-column editors.
I included a couple of screenshots showing how much space is wasted if the document is being edited in full-screen mode.

<figure>
    <img src="/assets/multicolumn/retina.png">
    <figcaption>Full screen retina (13 inch)</figcaption>
</figure>

<figure>
    <img src="/assets/multicolumn/4k.png">
    <figcaption>Full screen 4k (55 inch)</figcaption>
</figure>

My point was that as screens and resolutions get bigger, there are times when it makes sense to scroll code horizontally, rather than vertically. Before I address this argument further, let me clear up confusion between multi-column editing and existing mechanisms such as multi-pane and multi-view editing.



### Multi-column editors are not the same as multi-pane or multi-view editors

Almost universally, the readers thought I was talking about **multiple pane** editors, where more than one file is open and tiled next to each other.

<figure>
    <img src="/assets/multicolumn2/eclipse_multipane.png">
    <figcaption>Two files, next to each other in Eclipse</figcaption>
</figure>

Others pointed me to the ability in some editors to open **multiple views** into the same file. Notice that the two view scroll independently.

<figure>
    <iframe width="640" height="360" src="https://www.youtube.com/embed/xB_M9LZRdyc?rel=0" frameborder="0" allowfullscreen></iframe>
    <figcaption>Same file, multiple views, in Eclipse</figcaption>
</figure>

I am not an emacs user but **["follow-mode"] (http://www.gnu.org/software/emacs/manual/html_node/emacs/Follow-Mode.html)** for emacs was suggested a few times. This does get much much closer to what I need but the interface is still not very smooth. For example, I have to explicitly set the number of columns. If my screen is very wide, I increase the columns, if very small, go back to a single column, etc.

<figure>
    <iframe width="640" height="360" src="https://www.youtube.com/embed/JZtYALA-4n4?rel=0" frameborder="0" allowfullscreen></iframe>
    <figcaption>Follow-mode in emacs</figcaption>
</figure>

Someone also pointed me to a stack over flow post about **Vim's [scrollbind] (http://stackoverflow.com/a/5131298/46799)**. Incidentally, the linked question is my own question I asked back in Feb, 2011! I'm not a regular user of Vim either and scrollbind's limitation feel similar to emacs follow-mode limitations.

<figure>
<iframe width="640" height="360" src="https://www.youtube.com/embed/_b7rqyXNtE4?rel=0" frameborder="0" allowfullscreen></iframe>
    <figcaption>Scrollbind in Vim</figcaption>
</figure>



### An attempt to describe a multi-column editor

I have had a surprisingly difficult time finding an example editor which displays a single file in multiple columns, to take advantage of modern wide screen monitors. MS Word has allowed multi-column editing, unfortunately I'm on a mac and don't have access to Word. The best and the most obvious example from the offline world is a magazine layout:

<figure>
    <img src="/assets/multicolumn2/Magazine-Layout-Design-Inspiration-21.jpg">
    <figcaption>Image from inspirationhut.net, see footnote [1] for full url.</figcaption>
</figure>

The closest example to what a multi-column editor should look like is [this](assets/multicolumn2/multicolumncode.htm) example I wrote using css3's column-width attribute. I've included a short video below of what that page looks like (for those who don't have css3 browsers) and how it scrolls.

<figure>
<iframe width="640" height="360" src="https://www.youtube.com/embed/HMxwv3VyTm8?rel=0" frameborder="0" allowfullscreen></iframe>
    <figcaption>CSS3 based horizontal scaling</figcaption>
</figure>

Please ignore the fact that what I've linked above is not actually an editor! As I mentioned earlier, there don't seem to be any examples I can show. It displays static text, but does so in multiple columns. Several times I've taken a look at APIs for eclipse, netbeans and atom to attempt to add this functionality myself. It turns out that writing a blog post is easier than understanding the guts of IDEs.

### So why is this needed?

Refer to the first two screenshots, just notice that most of the space is wasted! This is the simplest argument in favor of multi-column editors. All else being equal, more code on screen is better.

There are a couple of interesting applications for writers, such as [OMM Writer] (http://www.ommwriter.com). This app "cuts away the clutter" letting writers concentrate on their words. Coders know a thing or two about concentrating on code, the ability to see more of it on screen doesn't hurt. However, coders are not writers. We need to to edit code in one window, perhaps monitor one thing in a terminal window, another in a web page. In such situations 

<img src="/assets/multicolumn2/aspect_ratios.svg" width="50%" height="50%">


  Only when need to concentrate
  Complex logic
  Understanding someone else's code
  Distraction free, like ommwriter.com

  All else being equal, better to see more code on screen, not all can hold it in head

  Files should never be that large.
    Show visualization of existing code and how many lines of code they take

  Why don't you use this one product?
    With modern resolutions and aspect ratios, this needs to be a widely available option. It would be silly if we had to use one or two products to get syntax highlighting.

[1] http://inspirationhut.net/inspiration/42-excellent-examples-of-magazine-layout-design-for-your-inspiration/
