from multiprocessing import Pool
import pandas as pd
import statistics
import csv
import os



# Reading summarized ads.txt and sellers.json file at global level for it to be usable directly in all functions
adstxt_summaryfile_path = os.path.join(os.path.join("..", "ads.txt-crawler"), "summary_adstxt.csv")
dfa = pd.read_csv(adstxt_summaryfile_path)

sellersjson_summaryfile_path = os.path.join(os.path.join("..", "sellers.json-crawler"), "summary_sellersjson.csv")
dfs = pd.read_csv(sellersjson_summaryfile_path)



def correct_direct_relationship(addom, sid):
	'''
	Detecting Case 1: Correct Direct Relationship
	'''
	global dfs;
	stype = ["PUBLISHER", "publisher", "Publisher", "BOTH", "Both", "both"]
	case_count = len(dfs[(dfs["ad_domain"].isin([addom, addom.lower()])) & (dfs["seller_id"].isin([sid, sid.lower(), sid.upper()])) & (dfs["seller_type"].isin(stype))])
	if case_count > 0:
		return 1
	else:
		return 0



def misrepresented_direct_relationship(addom, sid):
	'''
	Detecting Case 2: Misrepresented Direct Relationship
	'''
	global dfs;
	stype = ["INTERMEDIARY", "intermediary", "Intermediary"]
	case_count1 = len(dfs[(dfs["ad_domain"].isin([addom, addom.lower()])) & (dfs["seller_id"].isin([sid, sid.lower(), sid.upper()])) & (dfs["seller_type"].isin(stype))])
	
	case_count = case_count1
	if case_count > 0:
		return 1
	else: 
		return 0



def correct_reseller_relationship(addom, sid):
	'''
	Detecting Case 3: Correct Reseller Relationship
	'''
	global dfs;
	stype = ["INTERMEDIARY", "intermediary", "Intermediary", "BOTH", "Both", "both"]
	case_count = len(dfs[(dfs["ad_domain"].isin([addom, addom.lower()])) & (dfs["seller_id"].isin([sid, sid.lower(), sid.upper()])) & (dfs["seller_type"].isin(stype))])
	if case_count > 0:
		return 1
	else: 
		return 0



def misrepresented_reseller_relationship(addom, sid):
	'''
	Detecting Case 4: Misrepresented Reseller Relationship
	'''
	global dfs;
	stype = ["PUBLISHER", "publisher", "Publisher"]
	case_count = len(dfs[(dfs["ad_domain"].isin([addom, addom.lower()])) & (dfs["seller_id"].isin([sid, sid.lower(), sid.upper()])) & (dfs["seller_type"].isin(stype))])
	if case_count > 0:
		return 1
	else: 
		return 0



def fabricated_seller_ids(addom, sid):
	'''
	Detecting Case 6: Fabricated Seller IDs
	'''
	global dfs;
	unique_sids = dfs[(dfs["ad_domain"].isin([addom, addom.lower()])) & (dfs["sellerjson_presence"] == "Yes")]["seller_id"].unique().tolist()
	if (sid in unique_sids) or (sid.lower() in unique_sids) or (sid.upper() in unique_sids) or len(unique_sids) == 0:
		return 0
	else:
		return 1



def nonexistent_sellers_json(addom):
	'''
	Detecting Case 7: Non-existent sellers.json
	'''
	global dfs;
	unique_sdoms = dfs[(dfs["sellerjson_presence"] == "Yes")]["ad_domain"].unique().tolist()
	if addom in unique_sdoms:
		return 0
	else:
		return 1



def duplicate_sids_with_conflicting_relationships(addom, sid):
	'''
	Detecting Case 8: Duplicate Seller IDs with conflicting relationships
	'''
	global dfs;
	stypes = dfs[(dfs["ad_domain"].isin([addom, addom.lower()])) & (dfs["seller_id"].isin([sid, sid.lower(), sid.upper()]))]["seller_type"].unique().tolist()
	if len(list(set(["BOTH", "Both", "both"]).intersection(set(stypes)))) > 0:
		return 0
	else:
		return 1



def check_exchange_bidding(addom, sid):
	'''
	Detecting Case 9: Google's Exchange/Open Bidding (EB/OB) entries
	'''
	global dfs;
	domain_names = dfs[(dfs["ad_domain"].isin([addom, addom.lower()])) & (dfs["seller_id"].isin([sid, sid.lower(), sid.upper()])) & (dfs["seller_domain"] == "google.com")]["seller_name"].unique().tolist()
	for name in domain_names:
		if ("via EB" in name) or ("via OB" in name) or ("EB" in name) or ("OB" in name):
			return 1
	return 0



def discover_misrepresentations(websites):

	global dfa;

	# Variable to store misrepresentation case counts
	write_data = []
	
	for domain in websites:
		
		dftemp = dfa[dfa["website_domain"] == domain]
		num_adstxt_entries = len(dftemp)
		# Direct labeled entries in ads.txt
		direct_entries = len(dftemp[(dftemp["seller_account_type"].isin(["DIRECT", "direct", "Direct"]))])
		# Reseller labeled entries in ads.txt
		reseller_entries = len(dftemp[(dftemp["seller_account_type"].isin(["RESELLER", "reseller", "Reseller"]))])

		# Inititalizing variables to store counts of different misrepresentation cases
		case1, case2, case3, case4, case5, case6, case7, case8, case9, case10 = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
		addoms_checked_for_multiple_entries, t_case10 = [], []

		for i in range(len(dftemp)):
			ad_domain = str(dftemp.iloc[i]["ad_domain"]).strip()
			seller_id = str(dftemp.iloc[i]["seller_id"]).strip()
			seller_type = str(dftemp.iloc[i]["seller_account_type"]).strip()

			if seller_type in ["DIRECT", "direct", "Direct"]:
				# Case 1
				t_case1 = correct_direct_relationship(ad_domain, seller_id)
				case1 += t_case1
				# Case 2
				t_case2 = misrepresented_direct_relationship(ad_domain, seller_id)
				case2 += t_case2

			if seller_type in ["RESELLER", "reseller", "Reseller"]:
				# Case 3
				t_case3 = correct_reseller_relationship(ad_domain, seller_id)
				case3 += t_case3
				# Case 4
				t_case4 = misrepresented_reseller_relationship(ad_domain, seller_id)
				case4 += t_case4

			# Case 5: Duplicate Entries
			t_case5 = len(dftemp[(dftemp["ad_domain"] == ad_domain) & (dftemp["seller_id"] == seller_id) & (dftemp["seller_account_type"] == seller_type)])
			t_case5 = 1 if t_case5 > 1 else 0
			case5 += t_case5

			# Case 6
			t_case6 = fabricated_seller_ids(ad_domain, seller_id)
			case6 += t_case6

			# Case 7
			t_case7 = nonexistent_sellers_json(ad_domain)
			case7 += t_case7

			# Case 8
			t_case8 = len(dftemp[(dftemp["ad_domain"] == ad_domain) & (dftemp["seller_id"] == seller_id)]["seller_account_type"].unique().tolist())
			t_case8 = duplicate_sids_with_conflicting_relationships(ad_domain, seller_id) if t_case8 > 1 else 0
			case8 += t_case8

			# Case 9
			if ad_domain != "google.com":
				t_case9 = check_exchange_bidding(ad_domain, seller_id)
				case9 += t_case9

			# Case 10
			if ad_domain not in addoms_checked_for_multiple_entries:
				domain_entries = len(dftemp[(dftemp["ad_domain"] == ad_domain)]["seller_id"].unique().tolist())
				addoms_checked_for_multiple_entries.append(ad_domain)
				if domain_entries > 1:
					t_case10.append((domain_entries-1))

		
		case10 = "NA" if len(t_case10) == 0 else statistics.mean(t_case10)
		
        # Appending misrepresentations associated with current domain in sellers.json
		print(domain, num_adstxt_entries, case1, case2, direct_entries, case3, case4, reseller_entries, case5, case6, case7, case8, case9, case10)
		row = [domain, num_adstxt_entries, case1, case2, direct_entries, case3, case4, reseller_entries, case5, case6, case7, case8, case9, case10]
		write_data.append(row)

	return write_data



def main():

	global dfa;

	# Parallelize misrepresentation computations with a pool of 3 agents, each having a chunk of size of 1 website until finished
	agents = 3
	chunksize = 1

	# Defining output file path
	output_file_path = os.path.join("", "adstxt_misrepresentations.csv")

	# Defining and writing header to output file
	header_str = "website_domain, adstxt_lines, case1_(correct_direct), case2_(incorrect_direct), total_direct, case3_(correct_reseller), case4_(incorrect_reseller), total_reseller, case5_(duplicate_entries), case6_(fabricated_sids), case7_(nonexistent_sjson), case8_(correct_direct), case9_(correct_direct), case10_(correct_direct)"
	header = header_str.split(", ")
	f_csv = open(output_file_path, 'w', encoding='UTF8')
	writer = csv.writer(f_csv)
	writer.writerow(header)

	# Distributing list of websites into chunks for parallel processing
	websites = dfa[(dfa["adstxt_presence"] == "Yes")]["website_domain"].unique().tolist()
	chunks = []
	for site in websites:
		current_chunk = []
		for i in range(chunksize):
			current_chunk.append(site)
		chunks.append(current_chunk)

	# Parallelizing misrepresentation computations
	with Pool(processes=agents) as pool:
		write_rows = pool.map(discover_misrepresentations, chunks, chunksize)

	# Writing the misrepresentation output to csv
	for outp_row in write_rows:
		writer.writerow(outp_row)



if __name__ == "__main__":
	main()
