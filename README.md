# Ad Inventory Fraud Measurement

This repository is associated with the measurement study based research titled "**The Inventory is Dark and Full of Misinformation:
Understanding the Abuse of Ad Inventory Pooling in the Ad-Tech Supply Chain**". In this work, for the first time, we study and measure different mechanisms employed in the ad-tech ecosystem to misrepresent the ad inventory in order to fraud the advertisers. We perform our study on a set of 669 misinformation websites as they are more prone to engage in this kind of ad fraud so as to deceive brands in monetizing their misinformative websites. However, this repository contains the template code to repeat the work done in our research for any set of websites. 

The dataset associated with our work can be accessed below. It can be used to reproduce the results detailed in our paper.\
**Dataset:** [OSF Project Repository](https://osf.io/hxfkw/?view_only=bda006ebbd7d4ec2be869cbb198c6bd5)  

For further details, please check out the research paper associated with this work.\
**Paper:** https://doi.org/10.48550/arXiv.2210.06654

We study Ad Inventory Fraud in three ways:
1. ads.txt misrepresentations
2. sellers.json misrepresentations
3. Dark Pooling

It is recommended to follow the same directory structure as used in the repository to avoid an errors. Primarily, all the Python dependencies required to run this project can be installed using the following command:
```
pip install -r requirements.txt
```

## ads.txt crawler

The ads.txt standard (introduced in 2017) aims to address ad slot inventory fraud by requiring each publisher domain to maintain an ads.txt file
at the root level directory (e.g., publisher.com/ads.txt). The ads.txt file should contain entries for all ad exchanges that are authorized to sell or resell the ad inventory of the publisher. Our work is based on [2021 IAB Specification](https://iabtechlab.com/wp-content/uploads/2021/03/ads.txt-1.0.3.pdf) for ads.txt. (**Note**: "ads" in "ads.txt" stands for `Authorized Digital Sellers`.)

In order to study these ads.txt misrepresentations, first step is to crawl ads.txt using the codes present in `ads.txt-crawler` directory.

1. Enter the list of _valid_ websites in the file `websites_to_crawl.txt` by adding each website on a new line.
2. Download the appropriate version of chrome webdriver corresponding to the current version of your chrome browser and OS from the following link and place it at the location as shown above.
   https://chromedriver.chromium.org/downloads 
3. Replace the executable `chromedriver` inside the `ads.txt-crawler` directory with the executable obtained by unzipping the downloaded file in Step 2.
4. Run ads.txt crawler using the following command to download ads.txt for your websites (wherever available). ads.txt will be downloaded in `ads.txt-crawler/adstxt` directory. The subset of websites for whom ads.txt was _not_ found are associated with "No" in the `adstxt_presence.txt` file:
   ```
   python crawl_adstxt.py
   ```
5. Next, the downloaded ads.txt files can be parsed and pre-processed to eliminate irrelevant text by running the following command. It will generate a unified summary file `summary_adstxt.csv` containing entries of all the ads.txt files downloaded in Step 4.
   ```
   python parse_adstxt.py
   ```


## sellers.json crawler

The sellers.json standard (introduced in 2019), aims to mitigate inventory fraud by requiring each AdX and SSP to maintain a sellers.json file at the root level directory (e.g., adx.com/sellers.json). This sellers.json file must contain an entry for each entity that may be paid for inventory purchased through an AdX — i.e., one entry for each partner that is an inventory source for the AdX. Our work is based on [2019 IAB Specification](https://iabtechlab.com/wp-content/uploads/2019/07/Sellers.json_Final.pdf) for sellers.json.

In order to study sellers.json misrepresentations, first step is to crawl sellers.json using the codes present in `sellers.json-crawler` directory. This is the most expensive crawler in terms of the amount of time it takes.

1. Considering that `ads.txt-crawler` was already set first and ran, `chromedriver` will be directly used from the path as per the above directory structure. Also, `crawl_sellersjson_recursively.py` (to be run as below) crawls sellers.json for all the distinct ad domains found in the `summary_adstxt.csv` during the first iteration. The crawler maintains a mapping of sellers to the presence of their sellers.json file in `sellersjson_presence.txt`. 
   ```
   python crawl_sellersjson_recursively.py
   ```
2. After each iteration, a summarized file is created for all the sellers.json files crawled until that point using the `parse_sellersjson.py` code internally called by `crawl_sellersjson_recursively.py`.
3. For second iteration onwards, all the seller domains with `seller_type` as {"_INTERMEDIARY_" or "_BOTH_"} that are extracted from `summary_sellersjson.csv` and uncrawled, are crawled anew.
4. Steps 2 and 3 are repeated for 5 iterations expecting that sellers.json of all possible sellers would have been crawled. `summary_sellersjson.csv` obtained after all 5 iterations contains entries for all the sellers.json files crawled in these 5 iterations.
5. If any unexpected failure happens at any iteration, then the crawl can be restarted from that iteration by changing the line `range(1, 6)` in `crawl_sellersjson_recursively.py` to `range(x, 6)`, where x is the iteration in which the failure occured.

**Note**: 
* _Best effort crawling attempt is made using the above codes. However, there could be instances where the crawled sellers.json is syntactically incorrect and has may fail being parsed by our code. All such sellers.json filenames which are downloaded but have incorrect JSON format are saved in the file `failed_sellers.txt`._ These files can be opened to manually correct the  syntactical sellers.json formatting and the above steps can be rerun.
* _Google has an extremely large number of sellers (5M+) in its sellers.json file, which is also hosted on a non-standard location: http://realtimebidding.google.com. So, its presence is hard-coded to "Yes" and the link has been opened on Safari to manually copy paste its entire content in `google_com.json` named file._


## Discovering misrepresentations

The following scenarios describe different misrepresentations in `ads.txt` file:

<p align="center">
  <img src="https://github.com/Yash-Vekaria/Ad-Inventory-Fraud-Measurement/files/9793766/adstxt-inventory-fraud-toy-examples.pdf">
</p>

The following scenarios describe different misrepresentations in `sellers.json` file:

<p align="center">
  <img src="https://github.com/Yash-Vekaria/Ad-Inventory-Fraud-Measurement/files/9793769/sellersjson-inventory-fraud.pdf">
</p>

The counts for above misrepresentations can be discovered in ads.txt and sellers.json files using the `summary_adstxt.csv` and `summary_sellersjson.csv` files respectively generated above. 

The following commands need to be run inside `Misrepresentations` directory:
1. **ads.txt misrepresentations**: Output file: `adstxt_misrepresentations.csv`
   `discover_adstxt_misrepresentations.py` has been parallelized using Python `multiprocessing` library because usually even for 5 websites, the `summary_sellersjson.csv` becomes very large and non-parallel processing can take more time. `chunksize` representing the number of websites to be assigned to each thread and `agents` representing the number of threads to be run in parallel are initialized inside the `main()` function. These should be customized as per the number of websites studied by you.
   ```
   python discover_adstxt_misrepresentations.py
   ``` 
2. **sellers.json misrepresentations**: Output file: `sellersjson_misrepresentations.csv`
   ```
   python discover_sellersjson_misrepresentations.py
   ```


## Discovering Pooling

Pooling is a common strategy to share resources in online advertising. One way to identify the occurrence of pooling is by noting a single AdX-issued ‘publisher ID’ shared by multiple publisher websites. Dark pools are pools in which publisher IDs are shared by organizationally-unrelated publishers (possibly of different reputations). Dark pooling is a kind of ad fraud where advertisers are deceived during real-time bidding to think that they are buying an ad inventory on a premium website for instance, while their ad ends-up being shown on a low-end website due to a collusion between the premium and the low-end publisher in this case. Pooling can be studied statically as well as dynamically when websites are visited in real-time. The following diagram shows different kind scenarios related to Pooling.

<p align="center">
  <img src="">
</p>

In order to study whether the websites under the study are involved in pooling, there should be a broader list of websites with whom they might share seller Ids. As a result, the Top 100K Tranco websites are used here, with the intuition that any website under study might want to pool their inventory with a reputable website. If required, any custom set of websites could be used instead of Top 100K.

The Top 100K Tranco websites are extracted from the Top 1M Tranco websites available at `https://tranco-list.eu/list/25749/1000000` and accesssed on 15th October 2022. 
3. Top 100K domains are pasted from this list in `top_100k_websites.txt` and `ads.txt-crawler` is ran on these Top 100K domains to download their ads.txt files (wherever available) in the directory `./ads.txt-crawler/adstxt_top100k/` To run `ads.txt-crawler` for Top 100K domains, comment and uncomment the following lines in `crawl_adstxt.py`. It is recommended to download and use the latest tranco ranked list of domains whenever performing this study by updating the `top_100k_websites.txt` file and re-crawling their ads.txt files. 
1. Lines to comment in `crawl_adstxt.py`:
   ```
   input_directory, input_filename = "..", "websites_to_crawl.txt"
   adstxt_presence_directory, adstxt_presence_filename = "", "adstxt_presence.txt"
   output_directory = "./adstxt/"
   ```
2. Lines to uncomment in `crawl_adstxt.py`:
   ```
   input_directory, input_filename = "..", "top_100k_websites.txt"
   adstxt_presence_directory, adstxt_presence_filename = "", "top100k_adstxt_presence.txt"
   output_directory = "./adstxt_top100k/"
   ```

### Static Pooling

Static Pooling involves studying the signs of collusion by analysing the static files of `ads.txt` of study websites and the Top 100K websites and the set of and `sellers.json` files. Follow the steps below:

1. In order to obtain the parent organization of each domain under our study as well as for the Top 100K tranco domains, Entity-Organization List provided by DuckDuckGo (DDG) in their `tracker-radar` repository is used. Since, this repository is huge, it is recommended to clone it in a temporary folder using the following command.
   ```
   git clone https://github.com/duckduckgo/tracker-radar.git
   ```
2. Once, cloning completes, cut the folder titled `entities` from the cloned repository and paste it inside the `Pooling` directory of the current project's folder. `entities` is referenced from this location by the `discover_static_pools.py` script. If it is placed at some other location, remember to change the location at the global variables defined in this script. The temporary folder can be deleted.
3. Now, the following command can be run to generate a file named `static_pools.csv` inside the `Pooling` directory. It contains all the pools discovered from the ads.txt files of study websites as well as Top 100K websites where more than 1 websites share the same seller Id. More details about this file can be obtained from our Dataset page.
   ```
   python discover_static_pools.py
   ```

### Dynamic Pooling

Dynamic Pooling involves studying the signs of collusion between two or more websites (i.e., existence of static pools) by actually visiting the websites under study in real-time, capturing all the bid request, responses and post data and analysing them to find the evidence of such a collusion. We collect this data as explained in the Methodology diagram above.

1. 

## Citation

If you find this work useful, please cite our research paper:

```
@misc{https://doi.org/10.48550/arxiv.2210.06654,
  doi = {10.48550/ARXIV.2210.06654},
  
  url = {https://arxiv.org/abs/2210.06654},
  
  author = {Vekaria, Yash and Nithyanand, Rishab and Shafiq, Zubair},
  
  keywords = {Cryptography and Security (cs.CR), Computers and Society (cs.CY), Networking and Internet Architecture (cs.NI), Social and Information Networks (cs.SI), FOS: Computer and information sciences, FOS: Computer and information sciences},
  
  title = {The Inventory is Dark and Full of Misinformation: Understanding the Abuse of Ad Inventory Pooling in the Ad-Tech Supply Chain},
  
  publisher = {arXiv},
  
  year = {2022},
  
  copyright = {Creative Commons Attribution 4.0 International}
}
```
