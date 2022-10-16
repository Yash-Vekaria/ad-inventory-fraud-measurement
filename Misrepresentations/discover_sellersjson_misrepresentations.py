import pandas as pd
import csv
import os
import re



# Reading summarized sellers.json file at global level for it to be usable directly in all functions
sellersjson_summaryfile_path = os.path.join(os.path.join("..", "sellers.json-crawler"), "summary_sellersjson.csv")
dfs = pd.read_csv(sellersjson_summaryfile_path)

# Path to sellersjson_presence.txt
sellersjson_presence_path = os.path.join(os.path.join("..", "sellers.json-crawler"), "sellersjson_presence.txt")
f = open(sellersjson_presence_path, "r")

# Obtaining the list of INTERMEDIARY/BOTH with sellers.json
mapping_list = f.read().split("\n")
sellers_w_json = [dom.split(", ")[0] for dom in mapping_list if dom.split(", ")[1] == "Yes"]
f.close()



def isValidDomain(str):
	'''
	Checking if the domain is a valid domain or not
	'''
	# Regex to check valid domain name. 
	regex = "^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\\.)+[A-Za-z]{2,6}"
	
	# Compile the Regex
	p = re.compile(regex)

	# If the string is empty return false
	if (str == None):
		return False

	# Return if the string matched the Regex
	if(re.search(p, str)):
		return True
	else:
		return False



def discover_misrepresentations(seller_domains):

	global dfs, sellers_w_json;

	# Variable to store misrepresentation case counts
	write_data = []

	for ad_domain in seller_domains:

		dftemp = dfs[dfs["ad_domain"] == ad_domain]
		num_sellersjson_entries = len(dftemp)
		
		# Obtaining datframe rows by seller_type
		publisher_entries = len(dftemp[(dftemp["seller_type"].isin(["PUBLISHER", "publisher", "Publisher"]))])
		intermediary_entries = len(dftemp[(dftemp["seller_type"].isin(["INTERMEDIARY", "intermediary", "Intermediary"]))])
		both_entries = len(dftemp[(dftemp["seller_type"].isin(["BOTH", "both", "Both"]))])

		# Inititalizing variables to store counts of different misrepresentation cases
		case1, case2, case3, case4, case5, case6, case7 = 0, 0, 0, 0, 0, 0, 0

		# Case 1: Invalid Seller Type
		case1 = len(dftemp) - (publisher_entries + intermediary_entries + both_entries)

		# Case 4: Count of Confidential Sellers
		case4 = len(dftemp[(dftemp['seller_is_confidential'] == True)])

		# Case 5: Duplicate Entries
		case5 = dftemp.duplicated(dftemp.columns.tolist(), keep='first').sum()

		# Case 6: Intermediaries without sellers.json
		intermediaries_found = dftemp[dftemp["seller_type"].isin(["INTERMEDIARY", "intermediary", "Intermediary", "BOTH", "both", "Both"])]["seller_type"].unique().tolist()
		'''
		json_presence = dfs[(dfs["sellerjson_presence"]=="Yes")]["ad_domain"].unique().tolist()
		case6 = len(set(intermediaries_found).difference(set(json_presence)))
		'''
		case6 = len(set(intermediaries_found).difference(set(sellers_w_json)))

		# Case 7: ID Sharing
		case7 = dftemp.duplicated(subset='seller_id', keep='first').sum()

		for i in range(len(dftemp)):

			seller_name = str(dftemp.iloc[i]["seller_name"]).strip()
			seller_domain = str(dftemp.iloc[i]["seller_domain"]).strip()

			# Case 2
			if not(isValidDomain(seller_domain)) or seller_domain in ["", "NA"]:
				case2 += 1

			# Case 3
			if isValidDomain(seller_name) or seller_name in ["", "NA"]:
				case3 += 1
		
		print(ad_domain, num_sellersjson_entries, case1, case2, case3, case4, case5, publisher_entries, intermediary_entries, both_entries, case6, case7)
		row = [ad_domain, num_sellersjson_entries, case1, case2, case3, case4, case5, publisher_entries, intermediary_entries, both_entries, case6, case7]
		write_data.append(row)

	return write_data



def main():

	global dfs;

	# Defining output file path
	output_file_path = os.path.join("", "sellersjson_misrepresentations.csv")

	# Defining and writing header to output file
	header_str = "ad_domain, sellersjson_lines, case1_(incorrect_seller_type), case2_(incorrect_seller_domain), case3_(incorrect_seller_name), case4_(confidential_seller), case5_(duplicate_entries), total_publishers, total_intermediaries, total_both, case6_(intermediaries_wo_sellersjson), case7_(id_sharing)"
	header = header_str.split(", ")
	f_csv = open(output_file_path, 'w', encoding='UTF8')
	writer = csv.writer(f_csv)
	writer.writerow(header)

	# Distributing list of websites into chunks for parallel processing
	seller_ad_domains = dfs[dfs["sellerjson_presence"] == "Yes"]["ad_domain"].unique().tolist()
	write_rows = discover_misrepresentations(seller_ad_domains)

	# Writing the misrepresentation output to csv
	for row in write_rows:
		output_row = [str(item) for item in row]
		writer.writerow(output_row)



if __name__ == "__main__":
	main()
