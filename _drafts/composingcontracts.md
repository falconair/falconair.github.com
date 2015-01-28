---
layout: post_page
title: Adventures in financial and software engineering
excerpt: This post describes how to implement a DSL for pricing financial contracts in Scala
comments: true
---
<link href="//maxcdn.bootstrapcdn.com/font-awesome/4.2.0/css/font-awesome.min.css" rel="stylesheet">
TODO:
-as an alternative to uml, display combinator icons:
0, 1, +, negate, *, until, anytime
-comment about 'until' replacing eventually and anytime (as in FRP)

Several years ago I read one of the most interesting papers ["How to write a financial contract"] (http://research.microsoft.com/en-us/um/people/simonpj/Papers/financial-contracts/contracts-icfp.htm), by Simon Peyton Jones and Jean-Marc Eber. This paper presents a domain specific language for describing financial instruments such as bonds, options and futures. This subject is bound to be interesting to those in the financial industry; however, the ideas are explained so beautifully that the paper should inspire all programmers. Many academic papers are jargon filled and difficult to comprehend for non-experts. Peyton-Jones and Eber (and Julian Seward in a earlier version of the paper) take the time to motivate the problem and craft explanations as if they actually care about the audience. They also published a [powerpoint slide deck] (http://research.microsoft.com/en-us/um/people/simonpj/Papers/financial-contracts/Options-ICFP.ppt) which further explains the problem of writing composable financial contracts by developing a similar DSL for cupcakes!

I am not an expert in this topic and have written this post as an 'experience report.' I have implemented the paper mentioned above in Scala as an exercise in learning functional programming as well as financial engineering. The code is still in development and I know of at least one computation which is returning non-sensical results. This text is an attempt to expose my understanding of the concepts to (constructive) criticism. If someone decides to write their own implementation, I hope my code will clarify some details. As with my [previous] (TODO) post, I attempt to explain the business concepts so even those outside the financial industry can understand and benefit from the code examples.


### Get a sense of what we are talking about

Before we delve any deeper, let's discuss a few simple instruments so are not only speaking in terms of abstractions.

<img src="/assets/composingcontracts/buy3.svg" height="42" width="42">
A bond is simply a loan. When you buy a bond issued by a company or a government, you are lending them money. In return, at a future date, they may offer to give your money back to you in a single payment, multiple small payments with a big chunk, small payments based on this interest rate or that, etc.

<img src="/assets/composingcontracts/urban.svg" height="42" width="42">
A stock gives you (a very small fraction of) ownership in a company. What's important for this project is that a stock has a price (see [previous blog] (TODO) for further details). At any time, you can sell that stock and receive cash (approximately) equivalent to the price of the stock.

<img src="/assets/composingcontracts/business154.svg" height="42" width="42">
A future is a promise to do a transaction at a later date. If you are a farmer, you may decide to sell your crop before you have harvested it. Doing this limits your risk, but also limits your profits. Note that a future contract does not mean anything by itself. A 'future' has to refer to and 'underlying' product which will be bought or sold at a later time.

<img src="/assets/composingcontracts/man268.svg" height="42" width="42">
An option is similar to a future, but adds 'optionality.' In other words, while a future binds you to a purchase or a sale, an option gives you the right to simply refuse a transaction. If you can only make the decision exactly on a specific date, such as option is referred to as a European option. If you can make the decision to buy or not by at anytime between now until some specific date, such contract is called an American option. There are a number of other variations, which will ignore for the sake of simplicity.


### What does this look like in software?

The diagram below, while overly simplified, isn't completely unknown to financial programmers. It takes well established definitions and hierarchies and translates them into a uml diagram.

<img src="/assets/composingcontracts/composingcontractsuml.png">


However, what happens if we want to add custom contracts?
<img src="/assets/composingcontracts/composingcontractsumlwunknowns.png">

Notice that the root Instrument object contains a 'value' method, which returns its current value. In most casses, each class will implement it's own valuation function. If, tomorrow, we discover a generelization, say Bond and anohter set of instruments can nicely fit under 'Fixed Incom' class, we will either be forced to break the existing hierarchy or ignore the new generelization.

### The combinator way
Peyton-Jones and Eber propose a completely different way of describing these contracts. They break up existing contracts into smaller pieces to find much more general and expressive pieces. When  combined, not only do these smaller units describe existing contracts, but are surprisingly effective at describing many custom and ad-hoc contracts.

Here are some examples:

```java
def usd(amount) = Scale(Const(amount),One("USD"))
def stock(symbol) = Scale(Lookup(symbol),One("USD"))
def buy(contract, amount) = And(contract,Give(usd(amount)))
def sell(contract, amount) = And(Give(contract),usd(amount))
def zcb(maturity, notional, currency) = When(maturity, Scale(Const(notional),One(currency)))
def option(contract) = Or(contract,Zero())
def europeanCallOption(at, c1, strike) = When(at, option(buy(c1,strike)))
def europeanPutOption(at, c1, strike) = When(at, option(sell(c1,strike)))
def americanCallOption(at, c1, strike) = Anytime(at, option(buy(c1,strike)))
def americanPutOption(at, c1, strike) = Anytime(at, option(sell(c1,strike)))

val msft = stock("MSFT")
```

### Implementation

Let's start with 'Contract' described below:

```haskell
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
```

If you hold contract <span class="token constant">One</span>, you are owed a dollar immediately (currency implications are ignored in this explanation, although not in the implementation). If you own <span class="token constant">Give(One())</span>, you owe someone a dollar right away (not a few days from now). If you own <span class="token constant">When(tomorrow,One())</span>, tomorrow someone will deposit a dollar in your account. If you own <span class="token constant">Anytime(next week, One())</span>, you have the right to get your dollar anytime, between now and next week.

To make this even simpler, notice how many of the combinators can be mapped to basic math. <span class="token constant">Zero</span> and <span class="token constant">One</span> are simple enough. <span class="token constant">Give</span> is just negation, <span class="token constant">And</span> is addition, <span class="token constant">Or</span> is Math.max(), <span class="token constant">Cond</span> is 'if ... else ...' and <span class="token constant">Scale</span> is multiplication of sorts. <span class="token constant">When</span> and <span class="token constant">Anytime</span> are only non-mathy items.

Note that I haven't implemented the <span class="token constant">Until</span> operator and <span class="token constant">When</span> and <span class="token constant">Anytime</span> take explicit dates, rather than the more generic <span class="token constant">Observable[Boolean]</span> in the referenced paper.

Scale requires further comment, since it takes an Observable as an argument, not just Contract. Much of finance deals with future events. Stocks goe up, interest rates drop, a butterfly in China flaps wings and corn prices drop in Latin America. The language described by Contract alone is not able to represent real-world events. Since real-world events are uncertain, we need a way to represent this uncertainty. The 'Observable' type manages this uncertainty for us...somehow. We can write contracts which depend on the price of Google's stock, a year from now: When(next year, Scale(GOOG price, One())), and let Observable handle the details.

```haskell
Observable is
  Const(c) -- Always returns c
  or Date() -- Always returns the date passed into observable
  or Lift1()
  or Lift2()
  or Lookup() -- Looks up real-world values
  or various math operators
```

Observables represent uncertain values across time. Think of an Observable as a function which takes a date, and returns a range of possible values. For example, if you want to know the price of GOOG six months from now, Observable will get that for you. However, since no one knows the actual future price, Observable will return a range of possible values. For the mathematically inclined, an Observable is a stochastic process. For a given date, it will return a random variable.

Const(10) will always return 10, no matter what date you pass in. Date() will simply return the date you pass in to it. Lookup("MSFT") will return Microsoft's future prices. Note that Lookup is not in the original papers, I added it so I could play around with equity derivatives.

LiftX functions may be confusing to non-functional programmers. Say, for whatever reason, you want to write a contract against the square root of MSFT prices. You will notice that there is no square root combinator in Observable. Lift2(+) will 'overload' the plus function so it will also operate on Observable values.

Just for completeness, let's paste the actual scala code here:

```haskell
package ComposingContracts {

  sealed trait Contract
  case class Zero() extends Contract
  case class One(currency: String) extends Contract
  case class Give(contract: Contract) extends Contract
  case class And(contract1: Contract, contract2: Contract) extends Contract
  case class Or(contract1: Contract, contract2: Contract) extends Contract
  case class Cond(cond: Obs[Boolean], contract1: Contract, contract2: Contract) extends Contract
  case class Scale(scale: Obs[Double], contract: Contract) extends Contract
  case class When(date: LocalDate, contract: Contract) extends Contract
  case class Anytime(date: LocalDate, contract: Contract) extends Contract

  abstract class Obs[A] {
    def +(that: Obs[A])(implicit n: Numeric[A]): Obs[A] = Lift2(n.plus, this, that)
    def -(that: Obs[A])(implicit n: Numeric[A]): Obs[A] = Lift2(n.minus, this, that)
    ...
  }
  case class Const[A](k: A) extends Obs[A]
  case class Lift[B, A](lifted: (B) => A, o: Obs[B]) extends Obs[A]
  case class Lift2[C, B, A](lifted: (C, B) => A, o1: Obs[C], o2: Obs[B]) extends Obs[A]
  case class DateObs() extends Obs[LocalDate]
  case class Lookup[A](lookup: String) extends Obs[Double]
}
```


### I'll buy a One
Contracts and observables are all the end user sees. This domain specific language is enough to describe a large number of existing financial contracts, standardized as well us bespoke (or so the paper claims, assuming my own simplifications or errors didn't render this useless). Note that the claim is NOT that this langauge will describe ALL financial contracts. For example, ["Certified Symbolic Management of Financial Contracts"] (http://www.pa-ba.net/pubs/entries/bahr14nwpt.html) by Bahr, Berthold and Elsman extend this language with an accumulator conbinator to allow pricing of Asian options.


### What about computation?
I have talked a lot about representing contracts. As Peyton-Jones and Eber point out, this, by itself, is quite remarkable. Such a descriptive language can be used to communicate effectively among companies, clients and regulators. However, what are the actual mechanics of pricing these contracts?

Before we get any further in the actual computation, let's emphasize one point. The language which represents our universe of contracts has already been described. Nothing in the rest of this post will extend or modify that language. We now start the process of implementing the machinery which will price these contracts. Not only will the constructs of this machinery be invisible to end-users, we can swap out the existing implementation with a completely different mathematical model.

As the paper mentions, there are several ways of pricing financial contracts, including the lattice model, monte carlo and finite differences. The authors describe the lattice model in greater detail than the other two methods. I also implemented the same since monte carlo and finite difference made even less sense than what I was able to learn the lattice method.

### What's it worth?
Let's delve a bit deeper into a fundamental concept, how to find a fair price for financial contracts. Wall Street employees so many people with math and science backgrounds that they have their own name: quants. People have won nobel prizes and earned billions of dollars by answering the question of pricing these contracts. Naturally, we will discuss the most basic concepts.

#### A dollar today is worth more than a dollar tomorrow
How much are a thousand dollars worth? A thousand dollars! If you lend someone a thousand dollars for a year, how much should you charge them? The simplest answer is, you should charge them at least the thousand you are lending, plus at least as much as you would have earned if you just left that thousand bucks in your bank account.

In order to know how much a future dollar is worth, you need to know how far away that future is, and interest rates during that time.

#### Future's uncertain
We can not predict the future, but can build models which take uncertainty into account. For this post, we will use a simple model of future prices.

_Given today's price, tomorrow's price will either rise or drop proportional to volatility._

If an interest rate or a stock is S today and historically it has moved up by 'u' or down by 'd'', tomorrow it will be uS or dS, the day after it will be u^2S, d^2S or udS and so on. Why only two prices for tomorrow, instead of three or 8? Because this is the binomial lattice method, not trinomial or octnomial lattice method. Those who already know this method should note that we are ignoring probabilities here.

<img src="/assets/composingcontracts/binomiallattice.svg" >

<img src="/assets/composingcontracts/mappingdiagram.png"/>

If you ask this data structure for today's price, it will give you a single value, since that is already known. If you ask for any future dates, it will give you a range of values. In this specific model, day two will give you two values, day 10 will give you 10 values. The data structure is generally implemented as an list of arrays. If the whole lattice just contains a single number, we don't bother using arrays and just return that constant. A few more such optimizations are made.

Note that with the popularization of machne learning, probabilistic programming has become a hot topic, and with good reason. This is an extremely interesting subject, so much so that I recently enrolled in a Master's degree program at U Of Chicago to study this stuff. However, the existing implementation not not very elegant, general...or even completely correct.

```scala
trait BinomialLattice[A]{
  //apply functions allows this object to be 'called' as if it was a function
  def apply(i:Int):RandomVariable[A]
  //convenience 'apply' method allows use to think in terms of days, rather than just a integer index
  def apply(date:LocalDate):RandomVariable[A] = apply(ChronoUnit.DAYS.between(LocalDate.now(),date).toInt)
  def zip[B]...
  def map[B]...
  ...
}
//Actualy lattice structure needs to be bounded, otherwise implementation becomes very complex
trait BinomialLatticeBounded[A] extends BinomialLattice[A]{
  def size():Int
  ...
}
//If a value remains same, we can save memory by using ConstantBL
class ConstantBL[A](k:A) extends BinomialLattice[A]{
  override def apply(i:Int) = (j:Int)=>k
}
//Not quite ConstantBL, but deterministic
class PassThroughBL[A](func:(LocalDate)=>RandomVariable[A]) extends BinomialLattice[A]{
  override def apply(i:Int) = apply(LocalDate.now().plusDays(i))
  override def apply(i:LocalDate) = func(i)
}
class PassThroughBoundedBL[A](func:(LocalDate)=>RandomVariable[A], _size:Int) extends PassThroughBL[A](func) with BinomialLatticeBounded[A]{
  override def size() = _size
}
//Given a starting price and an up factor, generate the whole lattice
//NOTE: volatility is translated to up/down factor using a standard formula
class GenerateBL(_size:Int, startVal:Double, upFactor:Double, upProbability:Double=0.5) extends BinomialLatticeBounded[Double]{
  val cache = new ListBuffer[Array[Double]]
  val downFactor:Double = 1.0/upFactor

  cache.insert(0,Array(startVal))
  for(i <- 1 to size()-1){
    val arr = new Array[Double](i+1)
    arr(0) = downFactor * cache(i-1)(0)
    for(j <- 1 to i){
      arr(j) = upFactor * cache(i-1)(j-1)
    }
    cache.insert(i,arr)
  }
  override def apply(i:Int) = cache(i)
  override def size() = _size
}

//Given values of a lattice at the final date, apply function backwards towards start date
//Think of a discounting function, which takes future prices and uses interest rates to calculate current value
class PropagateLeftBL[A:ClassTag](source:BinomialLatticeBounded[A], func:((A,A)=>A)) extends BinomialLatticeBounded[A]{
  val cache = new ListBuffer[Array[A]]

  for(i <- 0 to size-1) cache.insert(i, new Array[A](i+1))

  for(i <- (0 to size-1).reverse){
    for(j <- (0 to i)){
      val x = source(i+1)(j)
      val y = source(i+1)(j+1)
      cache(i)(j) = func(x,y)
    }
  }

  override def apply(i:Int) = if ( size() > 1) cache(i) else source(i)
  override def size() = if (source.size() > 1) source.size()-1 else 1
}
```

A couple of supporting functions. _binomialPriceTree_ takes a starting price, date range and volatility and converts it to a binomial lattice. Note this is very similar to the GenerateBL class. The only difference here is that _binomailPriceTree_ converts volatility ot up/down factors. _dicount_ method takes two lattices, one contains the data which needs to be discounted and the second contains the interest rates which will be used to do the discounting.

```scala
def binomialPriceTree(days:Int, startVal:Double, annualizedVolatility:Double, probability:Double=0.5):BinomialLatticeBounded[Double] = {

  val businessDaysInYear = 365.0
  val fractionOfYear = (days* 1.0) divide businessDaysInYear
  val changeFactorUp = vol2chfactor(annualizedVolatility,fractionOfYear)
  val process = new GenerateBL(days+1,startVal,changeFactorUp)
  process
}

def vol2chfactor(vol:Double, fractionOfYear:Double) = {
  Math.exp(vol * Math.sqrt(fractionOfYear))
}

def discount(toDiscount:BinomialLatticeBounded[Double], interestRates:BinomialLattice[Double]):BinomialLatticeBounded[Double] = {
  val averaged = new PropagateLeftBL[Double](toDiscount, (x,y)=>(x+y) divide 2.0)//assume .5 probability
  val zipped = averaged.zip(interestRates)
  zipped.map[Double](avg_ir=>{
    val avg = avg_ir._1
    val ir = avg_ir._2
    avg/(1.0+ir)
    })
}
```


### Tie them together
We have seen the contract description language and some gory details of how a binomial lattice is implemented. We don't yet have a path connecting the two. Contract and Observable, both, are translated to a lower level abstract layer called PROpt, meaning "process optimization layer." A process, as mentioned earlier, represents a time varying value. Given a date, a process returns a random variable. BinomialLattice implements this, but PROpt is a layer between Contract/Observable and BinomialLattice.

---
<div>Icons made by <a href="http://www.freepik.com" title="Freepik">Freepik</a> from <a href="http://www.flaticon.com" title="Flaticon">www.flaticon.com</a> is licensed under <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0">CC BY 3.0</a></div>

Binomial lattice from http://stackoverflow.com/a/20911612/46799
