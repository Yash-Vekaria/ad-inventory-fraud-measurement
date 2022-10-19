import csv
import os



def extract_brands(crawls, path):
	'''
	Function to extract brands names for each website present in all the crawls supplied in the "crawls" variable
	The brands are extracted from the folder named as "<crawl_number>|brand|<website>|<crawl_date>.txt"
	'''

	website_to_brand_mapping = {}

	for crawl in crawls:
		website_folders = os.listdir(os.path.join(path, crawl))
		
		for website in website_folders:
			if website == ".DS_Store":
				continue
			crawl_files = os.listdir(os.path.join(os.path.join(path, crawl), website))
			
			for file in crawl_files:
				current_website = ""
				
				if "|brand|" in file:
					filepath = os.path.join(os.path.join(os.path.join(path, crawl), website), file)
					f = open(filepath, "r")
					lines = f.read().split("\n")
					
					if len(lines) != 0:
						current_website = str(website).replace("_",".")
						
						if current_website not in website_to_brand_mapping.keys():
							website_to_brand_mapping[current_website] = []
					
					for line in lines:
						if line.strip() == "":
							continue
						current_brand = line.strip().split(", ")[1].strip()

						if current_brand not in website_to_brand_mapping[current_website]:
							website_to_brand_mapping[current_website].append(current_brand)

	website_brand_pairs = []
	for website in website_to_brand_mapping.keys():
		for brand in website_to_brand_mapping[website]:
			pair = [website, brand]
			website_brand_pairs.append(pair)

	return website_brand_pairs



def main():

	# List names of all crawl folder from which advertising brands need to be extracted
	# Example: ["crawl_1", "crawl_2", "crawl_3"]
	crawls_to_summarise = ["crawl_sample"]

	# Path to the dynamic crawl directory containing the folders listed in "crawls_to_summarise" variable
	dynamic_crawl_directory = os.path.join(os.path.join("..", "Pooling"), "dynamic-crawler")

	# Path to store the output CSV
	output_filepath = os.path.join(os.path.join("", "brands.csv"))

	# Extract <website, advertiser> pairs
	website_brand_pairs = extract_brands(crawls_to_summarise, dynamic_crawl_directory)

	# Write the output to a CSV file
	header_str = "website_domain, advertising_brand"
	header = header_str.split(", ")
	f_csv = open(output_filepath, 'w', encoding='UTF8')
	writer = csv.writer(f_csv)
	writer.writerow(header)

	for row in website_brand_pairs:
		writer.writerow(row)



if __name__ == "__main__":
	main()