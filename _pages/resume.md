---
layout: page
permalink: /resume
title: Resume
tagline: Trading system developer and machine learning enthusiast
description: Resume
---

# Shahbaz Chaudhary

### Automated Trading System Developer And Machine Learning Enthusiast

### shahbazc@gmail.com

### 201-736-0282

### Profile
Experienced financial systems developer with an interest in non-mainstream solutions, data analytics, machine learning and programming language theory

### Projects
- Internet app: http://fixparser.targetcompid.com
Well regarded application to parse FIX messages into a human readable format. Does intelligent detection of delimiter (\01, pipe, comma, etc.), maintains order relationships, allows filters, etc.
- Internet app: http://datafa.me 
Web application to make it easy for users to analyze data. Maps data attributes to x and y axis, color, size, etc.
- Internet app: http://rule605.targetcompid.com
A major website which will display data collected due to SEC rule 605: statistics for broker order information.

- Open source: Tag library to make it easy for end-users to display statistical charts on the web (https://github.com/falconair/dimple-chart )
- Open source: Various open source FIX engines at https://github.com/falconair/[nodefix,fix.js,lowlevelfix]
- Open source: Submitted an experimental Qpid (http://qpid.apache.org) to Excel bridge.  This C# code implemented Excel’s RTD interface
- Open source: Various open source projects at https://github.com/falconair

- Blog: http://falconair.github.com

### Experience
- Software Engineer| Wolverine Trading| Chicago, IL| May ‘15-Present
  - Built a set of tools to latency and functional testing. Included components to pretend to by any exchange
  - Led a team which expanded this tool substantially
  - Introduced Hadoop/Spark to company for approximately 4 TB of data collected every day (given as first project to a newly formed team)
  - Part of market making engine team
  - Wrote tool to visualize complex strategies
  - All programming in C++

- Contractor | Bank Of America | Charlotte, NC | Sept’13-May ‘15
  - One of two software engineers in team of quants
  - Responsible for helping migrate processes from existing SQL/Java codebase to BofA’s proprietary Quartz system (derivative of Goldman Sachs’ SecDB/Slang)
  - Wrote reference data manager for corporate issued bonds and hedges (Fas133)
  - Used BofA's Quartz system (witten in python)

- Senior Developer | StreamingEdge | NY, NY | Apr’13-Aug’13
  - Responsible for Interest Rate Swap matching engine
  - Matching engine part of a low latency distributed system, interacting with historical data server, market data server, order entry platforms using high performance libraries such as Disruptor, Chronicle, various high speed collections.
  - Day to day operations include fixing bugs and improving performance

- Vice President | S. J. Levinson | Purchase, NY | Dec'09-Feb'13
  - Was one of two developers who wrote the algo container which contained strategy implementations, maintained parent/child order state, handled crash/recovery logic and interfaced with 3rd party OMSs such as Fidessa
  - Work with quants to translate their mathematical models to Java code, which were deployed in the algo container. Each logic update was thoroughly tested using test cases which used randomized input data and checked output against quant models.
  - Wrote first iteration of Pre-trade TCA (transaction cost analysis) API in Java and C#
  - Wrote and contributed to trading strategies in Java, such as VWAP, TWAP, IS
  - Contributed code to Fidessa's Java (Bluebox) interface between Fidessa OMS and in-house algo engine

- Term Structure Consultant | Marco Polo/Omega| New York, NY| Sept’07 - Dec'09
  - Designed and implemented a complete Java based trading system: broker interface (FIX 4.2, off-the-shelf order router, Interactive Brokers), market data interface (Bloomberg and Interactive Brokers), trading strategy infrastructure, several strategies and remote user interface to control/manage/monitor the trading system.
  - Traded the arbitrage strategy using the designed system.  Manually intervened on occasion.
  - Did post trade analysis
  - Wrote libraries to ease rapid development of strategies and efficient/quick execution of strategies: concurrency framework to make use of multiple cores without using any locks/semaphores (based on the Actor model as used by Erlang), event system for Java (as in C#).
  - Wrote a high-speed/low latency UDP based market data feed handler using MINA 2.0
  - Spent a month in Brazil writing feed handlers for Bovespa and BM&F
  - Did business side research on a cross-border arbitrage trade
  - Designed a system to take advantage of very short lived arbitrage opportunities
  - Designed and implemented a system to monitor high speed market data, orders and trades to calculate FIFO positions, currency adjusted P&L (realized/unrealized), exposure, hedge level, etc.
  - Programmed the market data feed monitor in Coral8 (stream database), the position manager in Java, post-trade data analysis in Python, visualization in R and some system proto types in C#
  - Experimented with a (partially successful) C# interface to Excel’s RTD interface
  - Wrote a Java and a C# interface to Bloomberg’s market data feed and two market data feeders for proprietary OMSs

- Term Structure Consultant | Wachovia Securities | Jersey City, NJ | Oct’06 – Sept’07
  - Implemented and maintained execution strategies for customer orders, along with a team of fellow developers
  - Helped maintain an execution strategy engine: a multi-threaded and event based java engine interfacing OMSs through the FIX protocol w/ custom fields
  - Worked with traders to resolve issues or potential bugs

- Term Structure Consultant | Goldman Sachs | Jersey City, NJ | Nov ’05 - May ’06
  - Changed GS’s client reporting infrastructure from one requiring java/sql/config edits for each new report to a more generic framework requiring a single config file,  enabling better scalability
  - Amended SWIFT reports to allow better and more reliable transmission of derivatives and debt data

- Term Structure Consultant | Jefferies Inc. | Jersey City, NJ | Sep ’04 - June ’05
  - Customized a P&L calculation algorithm: converted it from PL/SQL to T-SQL and adjusted it for the business environment at Jefferies (Brass equities trading system).
  - This P&L was calculated using a custom algorithm which used daily trades, security positions and firm P&L.  The same P&L was used by the top management (head-traders) on a daily basis to determine which customers contribute most or least profit to the firm's overall bottom line.
  - Wrote an ASP.NET web application to allow analysis of the calculated P&L.
  - Spent half the time speaking to business managers while the other half was spent implementing the algorithm (customized with their feedback), writing the web application and managing the database

- Term Structure Consultant | FXAll | New York, NY | Feb ’04 - Aug ’04
  - Wrote a Swing based quote monitor to display fast moving data in real-time with 'master-detail' data organization
  - Re-architected an existing Swing application to make it scale to rapidly increasing quantity of data.

- Term Structure Consultant | Bank Of America | New York, NY | Dec '03 - Feb '04
  - Wrote a message driven bean (JMS EJB on Weblogic) to allow parallel execution of tasks which sped up performance several fold.
Did detailed performance analysis of existing J2EE architecture and suggested points of improvement.

- Developer | UBS IB (Hedge Fund Risk) | New York, NY | Nov ‘02-Dec ‘03
  - Designed a Java object model for all instruments traded by the Hedge Fund Risk team, including equity, derivative, FI and FX instruments.
  - Designed and developed a Java API to read position/market data from flat files, databases and xml files, populate the instrument object model and feed to VaR engine.
  - Wrote a set of (simple) Sybase stored procedures to gather data to be used by the API mentioned above.
Did data gap analysis to find relevant attributes of CBs, wrote an Oracle SQL query which returned CB and associated cash flow schedules in the form of XML.
  - Developed a Java loader to read the XML feed for Convertible Bonds (CB), mentioned above, and convert it to BCP files to be read by a Sybase database.
  - Worked with a quant team member to implement the functionality of allowing ‘arbitrary market scenarios’ (stress tests) to be used by pricing and Value at Risk (VaR) engines.
  - Daily interaction with team members (and systems) distributed across: New York, Stamford, CT, London.

- Developer | Knight Securities | Jersey City, NJ | Sept ’00 - Aug ‘02
  - Technical lead in a team investigating business opportunities in the ECN business, along with a business strategist and a senior company lawyer.
  - Prototyped a small, real-time, multithreaded, order matching engine (mini-ECN) using Java, TIBCO
  - Worked with senior developers in designing a smart/intelligent order routing system using metrics such as speed, liquidity, etc. with real-time updates from various ECNs.
  - Designed and developed web-based decision support application using Java (JSP, servlets, JDBC), interactive charts with Sybase backend (maintaining over a million rows of data spread over a dozen tables) with Weblogic as the application server.
  - Managed two consultants who implemented a specialized system to provide fast access to company wide decision support systems.
  - Assisted senior management in evaluating future services/products by analyzing existing data and predicting future metrics.

### Education
- University Of Chicago| Masters in Analytics| 2015-2017
  - Combination of statistics and machine learning

- University Of Michigan | Bachelor of Science Computer Science | 1998 - 2000
  - Member of Business School E-Commerce Lab
  - Member of Artificial Intelligence Lab

- Western Michigan University | Kalamazoo, MI | Bachelor of Science Computer Science | 1996 - 1998
  - Member of Lee Honor’s College

- Publications
  - Jason M. Daida, Robert R. Bertram, Stephen A. Stanhope, Jonathan C. Khoo, Shahbaz A. Chaudhary, Omer A. Chaudhri, John Polito: What Makes a Problem GP-Hard? Analysis of a Tunably Difficult Problem in Genetic Programming. Genetic Programming and Evolvable Machines 2(2): 165-191 (2001)
  - Jason M. Daida, Shahbaz A. Chaudhary: Classification of Spectral Image Using Genetic Programming. GECCO 2000: 726-733

