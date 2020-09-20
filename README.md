# About theschoolofathens

The visualization is live [here](https://s4n0i.github.io/schoolofathens/).

## Why?
Philosophers don't think in isolation. They draw from their peers' work to make their own contribution, creating a web of ideas. The goal of this project was to make this visible using data analysis and visualization techniques.



This was inspired in part by similar work:



In [this](http://coppelia.io/2012/06/graphing-the-history-of-philosophy/) very nice article,
Simon Raper shows how he graphed the history of philosophy using philosopher's Wikipedia bio, in particular the "influenced" section.
He notes that the graph could be improved by taking into account indirect influences rather than just direct ones, which is what I tried here.  




[This](https://www.denizcemonduygu.com/philo/browse/) project by Deniz Cem Önduygu is quite different in nature,
as the visualized information was compiled all by hand (which is amazing).

## How?

### Scraping the data
Using the alphabetic index of philosophers as a starting point,
I parsed the "bio card" to get information about a philosopher and their influences.
To uniquely identify a philosopher, I used Wikipedia's pageid, as urls were often not unique.
Normalizing birth dates turned out to be a bit tricky.
It's not obvious how to express "500BC" in an amount of milliseconds since 1970. I settled for a conversion of
birth date string -> datetime64 -> 64bit signed integer of seconds before / after 1970.

### Building the graph of philosophers</h3>
After filtering some bad data points I found myself with a list of philosophers and their influences,
which could quite easily be turned into a directed graph.
I used the PageRank algorithm to get a measure of centrality for each node aka philosopher in the graph and stored the output as JSON.

### Visualization
The final step was to visualize the graph and its centrality scores in a d3.js force-directed graph.
A nice property of these graphs is that connected nodes are automatically drawn to each other, which leads to a natural clustering. Also its quite fun to drag around nodes.

## Disclaimer
This visualization carries quite some bias. The bias of looking only at the English Wikipedia,
the bias of looking only at philosophers with nicely scrapable bios,
the bias of the algorithm and hyperparameters used for calculating centrality scores
and lastly the noise added by my erratic Python programming.
If you still want to use it to draw conclusions like "Plato is #1 I knew it!!", go ahead.    

## References & Credit
This project uses
* [Wikipedia](https://www.wikipedia.org/) as its data source</li>
* [scrapy](https://scrapy.org/) for scraping</li>
* [networkx](https://networkx.github.io/) for calculating centrality scores</li>
* [d3.js](https://d3js.org/) for rendering the force-directed graph and axis</li>
* [materialize](https://materializecss.com/) for some UI elements</li>
