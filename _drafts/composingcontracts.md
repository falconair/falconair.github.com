---
layout: post_page
title: Adventures in financial and software engineering
comments: true
---
<link href="//maxcdn.bootstrapcdn.com/font-awesome/4.2.0/css/font-awesome.min.css" rel="stylesheet">

Several years ago I read one of the most interesting papers ["How to write a financial contract"] (http://research.microsoft.com/en-us/um/people/simonpj/Papers/financial-contracts/contracts-icfp.htm), by Simon Peyton Jones and Jean-Marc Eber. This paper presents a domain specific language for describing financial instruments such as bonds, options and futures. This subject is bound to be interesting to those in the financial industry; however, the ideas are explained so beautifully that the paper should inspire all programmers. Many academic papers are jargon filled and difficult to comprehend for non-experts. Peyton-Jones and Eber (and Julian Seward in a earlier version of the paper) take the time to motivate the problem and craft explanations as if they actually care about the audience. They also published a [powerpoint slide deck] (http://research.microsoft.com/en-us/um/people/simonpj/Papers/financial-contracts/Options-ICFP.ppt) which further explains the problem of writing composable financial contracts by developing a similar DSL for cupcakes!

I am not an expert in this topic and have written this post as an 'experience report.' I have implemented the paper mentioned above in Scala as an exercise in learning functional programming as well as financial engineering. The code is still in development and I know of at least one computation which is returning non-sensical results. This text is an attempt to expose my understanding of the concepts to (constructive) criticism. If someone decides to write their own implementation, I hope my code will clarify some details. As with my [previous] (TODO) post, I attempt to explain the business concepts so even those outside the financial industry can understand and benefit from the code examples.


### Get a sense of what we are talking about

Before we delve any deeper, let's discuss a few simple instruments so are not only speaking in terms of abstractions.

<img src="/img/buy3.svg" height="42" width="42">
A bond is simply a loan. When you buy a bond issued by a company or a government, you are lending them money. In return, at a future date, they may offer to give your money back to you in a single payment, multiple small payments with a big chunk, small payments based on this interest rate or that, etc.

<img src="/img/urban.svg" height="42" width="42">
A stock gives you (a very small fraction of) ownership in a company. What's important for this project is that a stock has a price (see [previous blog] (TODO) for further details). At any time, you can sell that stock and receive cash (approximately) equivalent to the price of the stock.

<img src="/img/business154.svg" height="42" width="42">
A future is a promise to do a transaction at a later date. If you are a farmer, you may decide to sell your crop before you have harvested it. Doing this limits your risk, but also limits your profits. Note that a future contract does not mean anything by itself. A 'future' has to refer to and 'underlying' product which will be bought or sold at a later time.

<img src="/img/man268.svg" height="42" width="42">
An option is similar to a future, but adds 'optionality.' In other words, while a future binds you to a purchase or a sale, an option gives you the right to simply refuse a transaction. If you can only make the decision exactly on a specific date, such as option is referred to as a European option. If you can make the decision to buy or not by at anytime between now until some specific date, such contract is called an American option. There are a number of other variations, which will ignore for the sake of simplicity.


### What does this look like in software?

The diagram below, while overly simplified, isn't completely unknown to financial programmers. It takes well established definitions and hierarchies and translates them into a uml diagram.

<img src="/img/composingcontractsuml.png">


However, what happens if we want to add custom contracts?
<img src="/img/composingcontractsumlwunknowns.png">

Notice that the root Instrument object contains a 'value' method, which returns its current value. In most casses, each class will implement it's own valuation function. If, tomorrow, we discover a generelization, say Bond and anohter set of instruments can nicely fit under 'Fixed Incom' class, we will either be forced to break the existing hierarchy or ignore the new generelization.

### The combinator way
Peyton-Jones and Eber propose a completely different way of describing these contracts. They break up existing contracts into smaller pieces to find much more general and expressive pieces. When  combined, not only do these smaller units describe existing contracts, but are surprisingly effective at describing many custom and ad-hoc contracts.

Let's start with 'Contract' described below:

<div style='overflow:scroll;'>
<pre><code class="language-haskell">
Contract is
  Zero -- This contract is worth $0.00
  or One -- $1.00
  or Give(Contract) -- -1 * value of Contract
  or And(Contract,Contract) -- Combine values of both contracts
  or Or(Contract,Contract) -- Maximum of two contracts
  or Cond(Observable,Contract,Contract) -- standard 'if' statement
  or Scale(Observbale,Contract) -- Multiply value of Contract by Observable
  or When(Date,Contract) -- On Date, value is Contract, else $0.0
  or Anytime(Date,Contract) -- From now until Date, value is Contract, else $0.0
</code></pre></div>

If you hold contract <span class="token constant">One</span>, you are owed a dollar immediately (currency implications are ignored in this explanation, although not in the implementation). If you own <span class="token constant">Give(One())</span>, you owe someone a dollar right away (not a few days from now). If you own <span class="token constant">When(tomorrow,One())</span>, tomorrow someone will deposit a dollar in your account. If you own <span class="token constant">Anytime(next week, One())</span>, you have the right to get your dollar anytime, between now and next week.

To make this even simpler, notice how many of the combinators can be mapped to basic math. <span class="token constant">Zero</span> and <span class="token constant">One</span> are simple enough. <span class="token constant">Give</span> is just negation, <span class="token constant">And</span> is addition, <span class="token constant">Or</span> is Math.max(), <span class="token constant">Cond</span> is 'if ... else ...' and <span class="token constant">Scale</span> is multiplication of sorts. <span class="token constant">When</span> and <span class="token constant">Anytime</span> are only non-mathy items.

Note that I haven't implemented the <span class="token constant">Until</span> operator and <span class="token constant">When</span> and <span class="token constant">Anytime</span> take explicit dates, rather than the more generic <span class="token constant">Observable[Boolean]</span> in the referenced paper.

Scale requires further comment, since it takes an Observable as an argument, not just Contract. Much of finance deals with future events. Stocks goe up, interest rates drop, a butterfly in China flaps wings and corn prices drop in Latin America. The language described by Contract alone is not able to represent real-world events. Since real-world events are uncertain, we need a way to represent this uncertainty. The 'Observable' type manages this uncertainty for us...somehow. We can write contracts which depend on the price of Google's stock, a year from now: When(next year, Scale(GOOG price, One())), and let Observable handle the details.

<div style='overflow:scroll;'>
<pre><code class="language-haskell">
Observable is
  Const(c) -- Always returns c
  or Date() -- Always returns the date passed into observable
  or Lift1()
  or Lift2()
  or Lookup() -- Looks up real-world values
  or various math operators
</code></pre></div>

Observables represent uncertain values across time. Think of an Observable as a function which takes a date, and returns a range of possible values. For example, if you want to know the price of GOOG six months from now, Observable will get that for you. However, since no one knows the actual future price, Observable will return a range of possible values. For the mathematically inclined, an Observable is a stochastic process. For a given date, it will return a random variable.

Const(10) will always return 10, no matter what date you pass in. Date() will simply return the date you pass in to it. Lookup("MSFT") will return Microsoft's future prices. Note that Lookup is not in the original papers, I added it so I could play around with equity derivatives.

LiftX functions may be confusing to non-functional programmers. Say, for whatever reason, you want to write a contract against the square root of MSFT prices. You will notice that there is no square root combinator in Observable. Lift(squareroot) will 'lift' the square root function so it will also operate on Observable values.

### I'll buy a One
Contracts and observables are all the end user sees. This domain specific language is enough to describe a large number of existing financial contracts, standardized as well us bespoke (or so the paper claims, assuming my own simplifications or errors didn't render this useless). Note that the claim is NOT that this langauge will describe ALL financial contracts. For example, ["Certified Symbolic Management of Financial Contracts"] (http://www.pa-ba.net/pubs/entries/bahr14nwpt.html) by Bahr, Berthold and Elsman extend this language with an accumulator conbinator to allow pricing of Asian options.

Follwing are some contracts defined in my implementation:

<div style='overflow:scroll;'>
<pre><code class="language-scala">
def usd(amount:Double) = Scale(Const(amount),One("USD"))
def buy(contract:Contract, amount:Double) = And(contract,Give(usd(amount)))
def sell(contract:Contract, amount:Double) = And(Give(contract),usd(amount))
def zcb(maturity:LocalDate, notional:Double, currency:String) = When(maturity, Scale(Const(notional),One(currency)))
def option(contract:Contract) = Or(contract,Zero())
def europeanCallOption(at:LocalDate, c1:Contract, strike:Double) = When(at, option(buy(c1,strike)))
def europeanPutOption(at:LocalDate, c1:Contract, strike:Double) = When(at, option(sell(c1,strike)))
def americanCallOption(at:LocalDate, c1:Contract, strike:Double) = Anytime(at, option(buy(c1,strike)))
def americanPutOption(at:LocalDate, c1:Contract, strike:Double) = Anytime(at, option(sell(c1,strike)))

def stock(symbol:String) = Scale(Lookup(symbol),One("USD"))
val msft = stock("MSFT")
</code></pre></div>

### What about computation?
I have talked a lot about representing contracts. As Peyton-Jones and Eber point out, this, by itself, is quite remarkable. Such a descriptive language can be used to communicate effectively among companies, clients and regulators. However, what are the actual mechanics of pricing these contracts?

Before we get any further in the actual computation, let's emphasize one point. The language which represents our universe of contracts has already been described. Nothing in the rest of this post will extend or modify that language. We now start the process of implementing the machinery which will price these contracts. Not only will the constructs of this machinery be invisible to end-users, we can swap out the existing implementation with a completely different mathematical model.

As the paper mentions, there are several ways of pricing financial contracts, including the lattice model, monte carlo and finite differences. The authors describe the lattice model in greater detail than the other two methods. I also implemented the same since monte carlo and finite difference made even less sense than what I was able to learn the lattice method.

### What's it worth?
Let's delve a bit deeper into a fundamental concept, how to find a fair price for financial contracts. Wall Street employees so many people with math and science backgrounds that they have their own name: quants. People have won nobel prizes and earned billions of dollars by answering the question of pricing these contracts. Naturally, we will discuss the most basic concepts.

#### A dollar today is worth more than a dollar tomorrow
How much is a US Dollar worth? A dollar! If this isn't non-sensical enough, how much are zero dollars worth? Obviously nothing.

If you lend someone a thousand dollars for a year, how much should you charge them? The most simple answer is, you should charge them at least the thousand you are lending, plus at least as much as you would have earned if you just left that thousand bucks in your bank account. Yes, you could have played the lottery with that money and won millions, but the likelyhood is extremely low. You could have invested that money in the stock market, but the returns still would have been uncertain. By leaving the money in the bank, you are essentially guaranteed the interest without any risk.

How much is a dollar worth a year or two years from now? We now know that this answer depends on the risk free interest rate and the duration of the loan. How much is a one $100 stock or a $100,000 house worth today, if you are guaranteed to receive ownership of these items in one year (at the quoted price)? Same 'discounting' idea applies.

#### Future's uncertain
We can not predict the future, but can build models which take uncertainty into account. For this post, we will use a simple model of future prices. _Whatever the price is today, tomorrow's price will either rise or drop by some amount, based on previous movements of prices._

If an interest rate or a stock is X today and historically it has moved up or down by a, tomorrow it will be X+a or X-a, the day after it will be X+a+a, X-a-a (and X+a-a, which is just X).
TODO diagram.

This is a simple model and one of the models mentioned by Peyton-Jones and Eber. Good enough for this implementation.

---
<div>Icons made by <a href="http://www.freepik.com" title="Freepik">Freepik</a> from <a href="http://www.flaticon.com" title="Flaticon">www.flaticon.com</a> is licensed under <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0">CC BY 3.0</a></div>
