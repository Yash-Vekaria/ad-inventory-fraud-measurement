import os
import json
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from parse_sellersjson import parse_sellersjson
from selenium.webdriver.chrome.options import Options



def get_chromedriver():
	'''
	Returns an instance of chromedriver
	'''
	# Download appropriate chromedriver from: https://chromedriver.chromium.org/downloads based on your chrome browser version
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	driver = webdriver.Chrome(executable_path="../chromedriver", options=chrome_options)
	return driver



def read_crawled_sellers(filepath):
	'''
	Reads and Returns websites from the file locations passed to it
	'''
	sites = []
	with open(filepath, "r") as f:
		sites = f.read().split("\n")
	f.close()
	sellers = [site.split(", ")[0] for site in sites]
	return sellers



def read_sellers_to_crawl(iteration_count, sellersjson_presence_filepath, summary_adstxt_path, summary_sellersjson_path):
	'''
	Reads and returns the list of sellers which have not yet been crawled
	'''
	sellers = []

	if iteration_count == 1:
		# If its the first iteration, distinct list of ad_domains is extracted from the summary_adstxt.csv
		df = pd.read_csv(summary_adstxt_path)
		ad_domains = df["ad_domain"].unique().tolist()
		sellers = [domain.strip().replace("https://","").replace("http://","").replace("www.","").lower() for domain in ad_domains]
	else:
		# For iteration second onwards, all distinct seller_domains are extracted from summary_sellersjson.csv until the point of previous iteration and uncrawled sellers are returned
		df = pd.read_csv(summary_sellersjson_path)
		seller_domains_found = []
		for i in range(len(df)):
			sellerjson_presence = str(df.iloc[i]["sellerjson_presence"])
			seller_type = str(df.iloc[i]["seller_type"]).upper()
			
			# A seller is expected to have a sellers.json file only if its seller_type is either INTERMEDIARY or BOTH. So, only those sellers are extracted from the summary file
			if sellerjson_presence == "Yes" and seller_type in ("BOTH","INTERMEDIARY"):
				seller_domain = str(df.iloc[i]["seller_domain"]).replace("https://","").replace("http://","").replace("www.","")
				seller_domain = str(seller_domain.strip().strip("/").strip(".").replace("/en/home","").replace("/en","").replace("/es","").replace("wwwmicro","www.micro").replace("/sellers.json","").replace("com.decenterads.ron","decenterads.com").replace("/push/spanish","").replace(" (Inherited: obox.com )", "").replace(" ","").replace("www.transmit.live","cdn.transmit.live").replace("com.originmedia.ron","originmedia.com").replace("corp.meitu.com","www.meitu.com").replace("www.stnvideo.com","cache.sendtonews.com").replace("com.vrtcal.ron","vrtcal.com").replace("com.vidillion.ron","vidillion.com").replace("/info","").replace("https://","").replace("http://","").replace("www.","").lower())

				# If seller_domain contains a long url with paths within the root directory, only the website url is retained
				if "/" in seller_domain:
					seller_domain = seller_domain[:seller_domain.index("/")]

				# Maintaining a list of only unique sellers
				if seller_domain not in seller_domains_found:
					seller_domains_found.append(seller_domain)

		# A: ad_domains are the ones whose sellers.json have already been crawled. So, extracting a list of all such unique ad_domains
		crawled_ad_domains = df["ad_domain"].unique().tolist()
		# B: The sellersjson_presence file contains mapping of all the sellers found until this point and that have been already attemped for extraction of sellers.json
		sellers_presence_file = read_crawled_sellers(sellersjson_presence_filepath)
		# Final list of uncrawled sellers is obtained by removing ad domains in A and B from the sellers extracted from summary_sellersjson.csv file
		sellers_ = list(set(seller_domains_found).difference(set(crawled_ad_domains)))
		sellers = list(set(sellers_).difference(set(sellers_presence_file)))

	print("Done extracting new ad domains to crawl!")
	return sorted(sellers)



def save_sellers_json(output_filepath, data):
	'''
	Saves the content of sellers.json inside the file location passed to it
	'''
	with open(output_filepath, 'w') as f:
		json.dump(data, f, indent=4)
	f.close()
	return



def crawl_sellersjson(output_directory, input_filepath, outpath_filepath, sellersjson_presence_filepath):
	'''
	Primary function to crawl all the sellers.json files recursively
	'''
	# Running 5 iterations to crawl sellers.json recursively. 
	# The range(1, 6) can be change to range(x, 6) if crawl failed at xth iteration
	for iteration in range(3, 6):

		print("Iteration #", iteration)
		# Obtain the list of unique uncrawled seller domains for which the sellers.json have to be crawled
		ad_domains_to_crawl = read_sellers_to_crawl(iteration, sellersjson_presence_filepath, input_filepath, outpath_filepath)

		# For the first iteration, sellersjson_presence.txt file is opened in write mode, but next iteration onwards, in append mode
		if iteration == 1:
			fm = open(sellersjson_presence_filepath, "w")
		else:
			fm = open(sellersjson_presence_filepath, "a")
			fm.write("\n")

		# Instantiate chromedriver
		driver = get_chromedriver()

		print("Domains to crawl in this iteration:", len(ad_domains_to_crawl))
		for site in ad_domains_to_crawl:

			print(site)
			termination_char = ""
			if ad_domains_to_crawl.index(site) != len(ad_domains_to_crawl)-1:
				termination_char = "\n"
			
			# Hard-coding google.com (having sellers.json at non-standard location: http://realtimebidding.google.com) to have sellers.json as "Yes". 
			# The google's sellers.json needs to be manually saved into "sellersjson" directory as "google_com.json"
			# Some problematic domains are also ignored
			if site in ["jp.pandora.tv","m.mediaday.co.kr","mediaday.co.kr"]:
				continue
			if site == "google.com":
				print(iteration, site + ", Yes")
				fm.write(str(site) + f", Yes{termination_char}")
				continue
			elif site in ["croooober.com"]:
				print(iteration, site + ", No")
				fm.write(str(site) + f", No{termination_char}")
				continue
			
			# Generating the standard URL storing sellers.json file for the current website
			site_sellersjson = "http://" + site + "/sellers.json"
			
			# If site domain is only digits then its not valid seller domain
			if site.isdigit():
				print(iteration, site + ", No")
				fm.write(str(site) + f", No{termination_char}")
				continue

			# Visit the sellers.json location on web
			try:
				driver.get(site_sellersjson)
			except:
				print(iteration, site + ", No")
				fm.write(str(site) + f", No{termination_char}")
				continue
			
			# Obtain the content of sellers.json
			html_str = driver.page_source
			try:
				soup = BeautifulSoup(html_str, features="html.parser")
				str_content = soup.get_text()
			except:
				print(iteration, site + ", No")
				fm.write(str(site) + f", No{termination_char}")
				continue
			
			# Each sellers.json has "sellers" key that contains all the sellers. In case this key is absent, its not a valid sellers.json file
			if "\"sellers\"" in str_content:
				filename = site.replace(".","_") + ".json"
				output_path = os.path.join(output_directory, filename)
				save_sellers_json(output_path, str_content)
				print(iteration, site + ", Yes")
				fm.write(str(site) + f", Yes{termination_char}")
			else:
				print(iteration, site + ", No")
				fm.write(str(site) + f", No{termination_char}")        

		driver.quit()
		fm.truncate()
		fm.close()
		
		# After crawling all the sellers.json from current iteration, they are parsed to create a unified summary_sellersjson.csv file
		parse_sellersjson(sellersjson_presence_filepath, outpath_filepath, output_directory)

	return



def main():

	# Enter the path to the file to store output about the presence of the sellers.json
	sellersjson_presence_directory, sellersjson_presence_filename = "", "sellersjson_presence.txt"
	sellersjson_presence_filepath = os.path.join(sellersjson_presence_directory, sellersjson_presence_filename)

	# Define path to store the input ads.txt summary file and output sellers.json summary file
	input_directory, input_filename = "../ads.txt-crawler", "summary_adstxt.csv"
	input_filepath = os.path.join(input_directory, input_filename)
	output_directory, output_filename = "", "summary_sellersjson.csv"
	outpath_filepath = os.path.join(output_directory, output_filename)
	
	# Define directory containing the crawled sellers.json files
	output_directory = "./sellersjson/"

	# Crawl sellers.json for the website list
	crawl_sellersjson(output_directory, input_filepath, outpath_filepath, sellersjson_presence_filepath)



if __name__ == "__main__":
	main()
