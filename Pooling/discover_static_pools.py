from collections import Counter
import pandas as pd
import json
import csv
import ast
import os
import re



# File path to the summary file of ads.txt of study domains
adstxt_summaryfile_path = os.path.join(os.path.join("..", "ads.txt-crawler"), "summary_adstxt.csv")

# File path to the summary file of sellers.json extracted for all the ad_domains discovered
sellersjson_summaryfile_path = os.path.join(os.path.join("..", "sellers.json-crawler"), "summary_sellersjson.csv")

# Read summary csv files for ads.txt and sellers.json
dfa = pd.read_csv(adstxt_summaryfile_path)
dfs = pd.read_csv(sellersjson_summaryfile_path, quotechar="\"")

# Global variables
study_domains, all_domains = [], []
static_pools, domain_to_parent_map = {}, {}

# Path to the ads.txt directory containing ads.txt files of the top 100K domains.
top100k_adstxt_directory = os.path.join(os.path.join("..", "ads.txt-crawler"), "adstxt_top100k")
# Path to the sellers.json directory
sellersjson_directory = os.path.join(os.path.join("..", "sellers.json-crawler"), "sellersjson")
# Path to the directory containing the entity-organization list downloaded from DDG tracker-radar Repo (https://github.com/duckduckgo/tracker-radar/tree/main/entities)
entity_dir = os.path.join("", "entities")



def process_seller_id(sellerid):
	'''
	Function to pre-process seller ids. The rules for processing defined in this function are inferred through manual inspection. You may add your own rules
	'''
	# Set of values in "seller_id" field that are incorrect/invalid
	incorrect_seller_id_values = ["pub_team_insert_pub_id_here", "id", "website id/publisher id", "supplyid", "xxxxxx", "abc%20local", "bauer%20media", "beliefnet", "big%20news%20site%201", "cbs%20local", "coedmedia", "entercom", "evolve%20media", "frankly", "horoscope.com", "hubbard%20radio", "merriam-webster", "prebid%20-%20pbh%20network", "prebid%20-%20smediavine", "purch", "usa%20today%20sports", "vox%20media", "wral", "aakljaan", "evfn2aah", "xxxx5", "xxxxxxxxxxx", "admin", "vk.vom", "your unique ads.txt id", "aca va el channel id", "nan", "reseller", "direct", "insert_your_vi_publisher_id_here", "reseller", "publisher id", "pui", "test.e-planning.", "badgirl", "spacedaily@gmail.com", "xxx", "xxx", "insert_udm_pid_here", "xxxxxxxxxxxxxxxxxxxx", "ahn3axrjaa==-a123", "ahn3axrjaa==-a14", "ahn3axrjaa==-a23", "ahn3axrjaa==-a61", "ahn3axrjaa==-a74", "q3n3axrjaa==-a162", "q3n3axrjaa==-a168", "q3n3axrjaa==-a184", "qnn3axrjaa==-a136", "qnn3axrjaa==-a141", "qnn3axrjaa==-a144", "rhn3axrjaa==-a144", "reseller", "nan", "switchconceptopenrtb", "xxxxxxxx", "backstage.pubid", "reseller", "switchconcepts", "pbn", "inr", "smt", "xxxxxx", "undefined", "xxxx-xxxx-01", "xxxx-xxxx-xx", "xxxxxxxxxx", "sell", "pubmatic.com", "pubid", "xxxxxx", "25ans_wedding_3_4", "media_id", "bali.idntimes.com", "banten.idntimes.com", "buzzfeed_amp", "buzzfeed_text_amp", "camphack.nap-camp.com", "cyclehack.jp", "duniaku.idntimes.com", "ejje.weblio.jp", "ejje.weblio.jp_amp", "elle_b_3_4", "ellegirl.jp_34", "harpersbazaar_jp_3_4", "jabar.idntimes.com", "jateng.idntimes.com", "jatim.idntimes.com", "jogja.idntimes.com", "kaltim.idntimes.com", "lampung.idntimes.com", "news.nifty.com", "nifty", "nifty_amp", "nifty_sdk", "ntb.idntimes.com", "runhack.jp", "sulsel.idntimes.com", "sumsel.idntimes.com", "sumut.idntimes.com", "thesaurus.weblio.jp_amp", "translate.weblio.jp", "tsurihack.com", "www.25ans.jp_3_4", "www.buzzfeed.com", "www.cosmopolitan.com_jp_3_4", "www.cosmopolitan.com_jp_amp_3_4", "www.esquire.com_3_4", "www.fujingaho.jp_3_4", "www.idntimes.com", "www.nifty.com", "www.popbela.com", "www.popmama.com", "www.womenshealthmag.com_3_4", "yamahack.com", "domainid", "xxxxx", "direct", "account id", "your_account_id", "your_site_id", "placeholder", "direct", "openx id", "reseller", "your_account_id", "omg zero", "mannenmedia", "ster", "weborama", "xxxx", "reseller", "aol.com", "nan", "your_publisher_id", "direct", "7xxxxx", "direct", "adwaveus", "atunwa", "audacy", "audioemotion", "audioone", "audioxi", "bauermedia", "cox", "coxmediagroup", "cumulus", "di", "entercom", "entravision", "hcode", "iheartmedia", "kriteria", "leanstreamdemand", "linkfire", "nextregie", "octave", "otherwortb", "pandora", "podiumaudio", "qmusic", "remixd", "rogers", "rpp", "sbs", "soundcloud", "speechkit", "talksport", "targetspot", "townsq", "trinityaudio", "tunein", "univision", "videobyte", "washingtonpost", "dax", "trinityaudio", "nan", "insert your uam pub id found here", "pub id", "nan", "switchconcepts", "your publisher id", "compass pub id", "number", "eduard", "reseller", "15xxxx", "seller_id", "spot_id", "direct", "direct", "direct", "*lkqdaccount*", "xxxxxx", "client uuid", "clientuuid", "****", "anuntis-es", "csnstores", "direct", "google.com", "lmc-digitalfirstmedia", "mobile-softoniccom", "olx-ua", "pub-", "reseller", "softonic", "tablet-softoniccom", "reseller", "quinstreet", "dmg", "&", "waytogrow/dominik.czarnota@waytogrow.eu", "waytogrow/janusz.michalik@waytogrow.pl", "switch", "direct", "reseller", "reseller", "____", "*publisher-id*", "pub 2320327466016366) -eb", "&lt;148395&gt;"]

	sid = sellerid.strip().lower().strip("\"")
	sid = sid.strip().strip(" ").strip("[").strip("]").strip("{{").strip("}}").strip("{").strip("}").strip("(").strip(")").strip("<").strip(">").strip().strip(" ")

	if sid in incorrect_seller_id_values:
		return "", False

	replace_map = {"\\capub-": "pub-", "ca-games-pub-": "pub-", "ca-mb-app-pub-": "pub-", "ca-pub-": "pub-", "mb-app-pub-": "pub-", "ca-video-pub-": "pub-", "dis841569": "841569", "video-pub-": "pub-", "partner-pub-": "pub-", "pub- ": "pub-", "pub7249223325809944": "pub-7249223325809944", "pub-pub-": "pub-", "ub-1283624027922691": "pub-1283624027922691", "b- 059922": "b-059922"}
	for mapping in replace_map.keys():
		sid = sid.replace(mapping, replace_map[mapping])

	replace_patterns = ["​", "â  ", "â ", "ã‚â ", "ăâ ", "directâ ", "resellerâ ", "â ", "آ ", "р  рір‚в„ў ", "ãƒâ€š ", "â ", "ã‚ ", "ãš ", " direct", "direct", "client ", "ξβξβ ", "ξ ", "ãš", "ãƒâ€šã‚â ", "1 ", "â€‹", "?", "tl ", "reseller", "*"]
	for pattern in replace_patterns:
		sid = sid.replace(pattern, "")

	replace_map = {"ma6m9pbvib: : 1363": "1363", "publisher_ 5171": "publisher_5171", "|1937|": "1937", "â¬â€ 440647": "440647", "ãƒâ€šã‚18222": "18222", "ã‚74d964d64622eda353dbb95047d88f16": "74d964d64622eda353dbb95047d88f16", "ã‚aab3b5904a4f1c27f53084dbb14945a1": "aab3b5904a4f1c27f53084dbb14945a1", "ã‚f15f921e8523dda73e32ff2a6069788f": "f15f921e8523dda73e32ff2a6069788f", "ã‚f963243b8472aa9474d37bb6173c4f18": "f963243b8472aa9474d37bb6173c4f18", "ă196713": "196713", "ă50": "50", "ăb-060443": "b-060443"}
	for mapping in replace_map.keys():
		sid = sid.replace(mapping, replace_map[mapping])

	if sid in ["pid", "property code", "publisher_id", "publisherid", "purch.com"]:
		return "", False

	return sid, True



def process_ad_domain(domain_str):
	'''
	Function to pre-process ad domains. The rules for processing defined in this function are inferred through manual inspection. You may add your own rules
	'''
	dom = domain_str.strip().lower().strip("\"")

	id_mappings = {"exponential.com 176430direct    afac06385c445926": ["exponential.com", "176430"], "google.comâ pub-491005001790614": ["google.com", "pub-491005001790614"], "google.comâ pub-491005001790614": ["google.com", "pub-491005001790614"], "aps.amazon.com 3854 reseller": ["aps.amazon", "3854"], "136839spotx.tv": ["spotx.tv", "136839"], "xad.com 241 reseller 81cbf0a75a5e0e9a": ["xad.com", "241"], "widespace.com - 8470 - direct": ["widespace.com", "8470"], "widespace.com - 8471 - direct": ["widespace.com", "8471"], "tsyndicate.com 32164": ["tsyndicate.com", "32164"], "tsyndicate.com 32207": ["tsyndicate.com", "32207"], "sonobi.com b24c93d5b8 direct": ["sonobi.com", "b24c93d5b8"], "smartadserver.com 3117 reseller": ["smartadserver.com", "3117"], "smartadserver.com 3668 reseller": ["smartadserver.com", "3668"], "sekindo.com 19327  direct": ["sekindo.com", "19327"], "rubiconproject.com 16824 reseller 0bfd66d529a55807": ["rubiconproject.com", "16824"], "rhythmone.com 1059622079 reseller": ["rhythmone.com", "1059622079"], "rhythmone.com 4201299756 reseller a670c89d4a324e47": ["rhythmone.com", "4201299756"], "roqoon.com 134034 reseller": ["roqoon.com", "134034"], "pokkt.com 5886 reseller c45702d9311e25fd": ["pokkt.com", "5886"], "openx.com 537106719 reseller 6a698e2ec38604c6": ["openx.com", "537106719"], "openx.com 537126269 reseller": ["openx.com", "537126269"], "openx.com 537149762 reseller 6a698e2ec38604c6": ["openx.com", "537149762"], "openx.com 540191398 reseller 6a698e2ec38604c6": ["openx.com", "540191398"], "openx.com 540421297 reseller 6a698e2ec38604c6": ["openx.com", "540421297"], "openx.com 540634022 reseller 6a698e2ec38604c6": ["openx.com", "540634022"], "openx.com537126269reseller": ["openx.com", "537126269"], "lockerdome.com12038519593865728direct": ["lockerdome.com", "12038519593865728"], "lkqd.com 423 reseller 59c49fa9598a0117": ["lkqd.com", "423"], "lijit.com 215294 reseller fafdf38b16bf6b2b": ["lijit.com", "215294"], "lijit.com 215294-eb reseller fafdf38b16bf6b2b": ["lijit.com", "215294-eb"], "indexexchange.com 184110 reseller": ["indexexchange.com", "184110"], "indexexchange.com 184270 reseller 50b1c356f2c5c8fc": ["indexexchange.com", "184270"], "indexexchange.com184110reseller": ["indexexchange.com", "184110"], "improvedigital.com 1129 reseller": ["improvedigital.com", "1129"], "improvedigital.com 1175 reseller": ["improvedigital.com", "1175"], "improvedigital.com 1225    reseller": ["improvedigital.com", "1225"], "improvedigital.com 1227     reseller": ["improvedigital.com", "1227"], "improvedigital.com 1267     reseller": ["improvedigital.com", "1267"], "gumgum.com 13244 direct ffdef49475d318a9": ["gumgum.com", "13244"], "google.com pub-4588688220746183 direct 5338762016": ["google.com", "pub-4588688220746183"], "google.com-pub": ["google.com", "pub-3805568091292313"], "freewheel.tv 1069 reseller": ["freewheel.tv", "1069"], "freewheel.tv 1076753 reseller": ["freewheel.tv", "1076753"], "freewheel.tv 1076769 reseller": ["freewheel.tv", "1076769"], "freewheel.tv 1091073 reseller": ["freewheel.tv", "1091073"], "freewheel.tv 1091089 reseller": ["freewheel.tv", "1091089"], "freewheel.tv 133681 reseller": ["freewheel.tv", "133681"], "freewheel.tv 133777 reseller": ["freewheel.tv", "133777"], "freewheel.tv 156113 reseller": ["freewheel.tv", "156113"], "freewheel.tv 1867 reseller": ["freewheel.tv", "1867"], "freewheel.tv 1873 reseller": ["freewheel.tv", "1873"], "freewheel.tv 1929 reseller": ["freewheel.tv", "1929"], "freewheel.tv 1931 reseller": ["freewheel.tv", "1931"], "freewheel.tv 1933 reseller": ["freewheel.tv", "1933"], "freewheel.tv 1937 reseller": ["freewheel.tv", "1937"], "freewheel.tv 5649 reseller": ["freewheel.tv", "5649"], "freewheel.tv 654226 reseller": ["freewheel.tv", "654226"], "freewheel.tv 654242 reseller": ["freewheel.tv", "654242"], "freewheel.tv 985441 reseller": ["freewheel.tv", "985441"], "freewheel.tv 985473 reseller": ["freewheel.tv", "985473"], "districtm.io 100962 reseller": ["districtm.io", "100962"], "engagebdr.com 16 reseller": ["engagebdr.com", "16"], "coxmt.com 2000067997102 reseller": ["coxmt.com", "2000067997102"], "coxmt.com 2000068024302 direct": ["coxmt.com", "2000068024302"], "coxmt.com2000067997102reseller": ["coxmt.com", "2000067997102"], "contextweb.com 560606 reseller": ["contextweb.com", "560606"], "contextweb.com 561481 reseller": ["contextweb.com", "561481"], "contextweb.com 561562 reseller 89ff185a4c4e857": ["contextweb.com", "561562"], "c1exchange.com c1x201401 reseller": ["c1exchange.com", "c1x201401"], "c1exchange.com c1x_a9_uampubs reseller": ["c1exchange.com", "c1x_a9_uampubs"], "174835 – direct – criteo.com": ["criteo.com", "174835"], "admanmedia.com 552 reseller": ["admanmedia.com", "552"], "adtech.com 10861 reseller": ["adtech.com", "10861"], "adtech.com 4687 reseller": ["adtech.com", "4687"], "aol.com       27093 reseller": ["aol.com", "27093"], "aol.com 46658 reseller": ["aol.com", "46658"], "aolcloud.net 10861 reseller": ["aolcloud.net", "10861"], "aolcloud.net 4687 reseller": ["aolcloud.net", "4687"], "advertising.com 22153 reseller": ["advertising.com", "22153"], "advertising.com 7574 reseller": ["advertising.com", "7574"], "appnexus.com 1908 reseller f5ab79cb980f11d1": ["appnexus.com", "1908"], "appnexus.com 2928 reseller": ["appnexus.com", "2928"], "appnexus.com 7944 reseller": ["appnexus.com", "7944"], "appnexus.com 8233 reseller": ["appnexus.com", "8233"], "bidmachine.io 36 reseller": ["bidmachine.io", "36"], "bidmachine.io 60 reseller": ["bidmachine.io", "60"], "pubmatic.com 120391 reseller 5d62403b186f2ace": ["pubmatic.com", "120391"], "pubmatic.com 156138 reseller": ["pubmatic.com", "156138"], "pubmatic.com 156248 reseller": ["pubmatic.com", "156248"], "pubmatic.com 156556 reseller": ["pubmatic.com", "156556"], "pubmatic.com 157150 reseller 5d62403b186f2ace": ["pubmatic.com", "157150"], "pubmatic.com 157743": ["pubmatic.com", "157743"], "pubmatic.com156138reseller": ["pubmatic.com", "156138"], "pubmatic.com156248reseller": ["pubmatic.com", "156248"], "pubmatic.com156556reseller": ["pubmatic.com", "156556"], "video.unrulymedia.com 1237114149": ["video.unrulymedia.com", "1237114149"], "rhythmone.com1683053691": ["rhythmone.com", "1683053691"], "pmp.adcrew.co  89ff185a4c4e857c": ["pmp.adcrew.co", "89ff185a4c4e857c"], "openx.com 540731760": ["openx.com", "540731760"], "increaserev.com 234233": ["increaserev.com", "234233"], "increaserev.com 234234": ["increaserev.com", "234234"], "increaserev.com 242412": ["increaserev.com", "242412"], "aol.com 57683": ["aol.com", "57683"],"appnexus.com/564": ["appnexus.com", "564"], "yahoo.com 58578": ["yahoo.com", "58578"], "spotxchange.com 249286": ["spotxchange.com", "249286"], "spotx.tv 108933": ["spotx.tv", "108933"], "spotx.tv 249286": ["spotx.tv", "249286"], "smartadserver.com 3050": ["smartadserver.com", "3050"], "rubiconproject.com 11560": ["rubiconproject.com", "11560"], "rubiconproject.com 17280": ["rubiconproject.com", "17280"], "rhythmone.com1683053691": ["rhythmone.com", "1683053691"], "openx.com 537149888": ["openx.com", "537149888"], "marsmedia. 102825": ["mars.media 102825", "102825"], "indexexchange.com 191730": ["indexexchange.com", "191730"], "indexexchange.com194527": ["indexexchange.com", "194527"], "improvedigital.com 1680": ["improvedigital.com", "1680"], "gothamads.com 126": ["gothamads.com", "126"], "gothamads.com126": ["gothamads.com", "126"], "google.com pub-4299156005397946": ["google.com", "pub-4299156005397946"], "google.com pub-7079691902491759": ["google.com", "pub-7079691902491759"], "districtm.io 100962": ["districtm.io", "100962"], "districtm.io 101760": ["districtm.io", "101760"], "emxdgt.com 1759": ["emxdgt.com", "1759"], "contextweb.com 560288": ["contextweb.com", "560288"], "adform.com 1889": ["adform.com", "1889"], "airpush.com 292001": ["airpush.com", "292001"], "aol.com    21364": ["aol.com", "21364"], "aol.com 58578": ["aol.com", "58578"], "advertising.com 29034": ["advertising.com", "29034"], "adyoulike.com 83d15ef72d387a1e60e5a1399a2b0c03": ["adyoulike.com", "83d15ef72d387a1e60e5a1399a2b0c03"], "appnexus.com 1019": ["appnexus.com", "1019"], "appnexus.com 1314": ["appnexus.com", "1314"], "appnexus.com 4009": ["appnexus.com", "4009"], "pubmatic.com 156078": ["pubmatic.com", "156078"], "pubmatic.com156631": ["pubmatic.com", "156631"],}
	if dom in id_mappings.keys():
		return id_mappings[dom][0], True, id_mappings[dom][1]
	
	incorrect_domain_values = ["ads.txt", "video", "video:", "video.", "video demand partners:", "vertamedia certification authority id - 7de89dc7742b5b11.", "verizon", "verizon/aol","usa today", "twitter", "test ads.txt", "terms of use", "terms and conditions", "termina", "telaria", "telaria.cyahoom", "teads", "t2est ads.txt", "support", "sticky ads (open marketplace) = freewheel", "sticky ads (deal)  - freewheel", "startapp.com smt reseller", "skip to content", "search", "rubicon ads.txt", "resources", "reseller", "quick links", "purch.com", "publishers", "privacy policy", "pricing", "press", "posumeads.com & pocketmath.com","portail orange", "portail orange reunion", "policies", "playground xyz", "partners", "optional reseller lines", "optional lines:", "opsco", "only include taboola for techcrunch & engadget", "ona for media services - adx emea", "oath", "netlink banner: adx partner", "nativo", "native demand partners:", "mowplayer", "linkedin", "google adsense", "home", "invoices", "inbox", "insticator", "features", "facebook.com", "eseller", "entry", "egami", "display", "disallow:", "direct", "daria", "cookies","contact", "contact: adops@interplaymedia.com.au", "contact us", "concat", "company", "cloud", "close", "checkout", "case studies", "careers", "calendar", "brightcom vdx", "bingo pop line items:", "search", "pub-2205121062140812", "pub-2603664881560000", "pub-2726428685015992", "pub-3132893725603935", "pub-7913044002918072", "pub-7915887679464005", "16189", "17250", "3563", "18 13132", "1813132", "1992", "22069", "22069", "256757", "458", "4ad745ead2958bf7", "560382", "59491", "60d26397ec060f98", "6796094", "6c8d5f95897a5a3b", "72av8h", "75547ba18f13f74", "7de89dc7742b5b11", "80media", "83e75a7ae333ca9d", "a14650a2-7db0-4d21-9666-4b1b9b32aa08", "a670c89d4a324e47", "f08c47fec0942fa0 lkqd.net", "f08c47fec0942fa0", "fcadx-55297863", "1371890", ".com", "ca-pub-8787923930478618", "ca-video-pub-8787923930478618", "0bfd66d529a55807", "smartx"]
	if dom in incorrect_domain_values:
		return "", False, "NA"
		
	# replaces patterns like: " [534]"
	dom = re.sub(" \[[0-9]+\]", "", dom)
	# replaces patterns that start with: "ads."
	dom = re.sub("^ads\.", "", dom)

	invalid_patterns = ["---", "contact=", "subdomain=", "*", "|| []", "nbsp;", "-optional", "- next", "//", "2021-", "33 across ", "29 julio", "29/11", "33across.com 001", "3test ", "4test ", "5 test ", "6 test ", "7 test ", "::", "<", "==", "___", "\\", "a.v ", "about", "account", "add your ", "ad te", "adnet 1", "adnet 2", "adnet 3", "adnet 4", "adnet 5", "adnet 6", "adnet 7", "adnet 8", "adnet 9", "-2021", " [", "@", "dx eb", " ads txt ", "/ads.tx", "ts ar", "er in", "er we", " - ", "/2021", "ï¼ƒfulct", "â€‹â€‹", "}", "{\\", "xandr appnexus.com", "version ", "nrx-pub-474a8699-70c2", "ads.txt information:", "thenewslens.com ", "ownerdomain=", "ownerdomain =", "owner =", "gtag(){", "gtag('js'", "ads.txt", "_adstxt_", "-2022", "ads: true", "arkonline.txt", "verification=", "customers", "facebook", "instagram.com", "projectionist", "test.test.com", "undefined"]
	for pattern in invalid_patterns:
		if dom.find(pattern) != -1:
			return "", False, "NA"

	replace_map = {"nsticator.com": "insticator.com", "a.twiago.com": "twiago.com", "ads-9dots.project-limelight.com/sellers.json": "project-limelight.com", "ads.9dots.project-limelight.com/sellers.json": "project-limelight.com", "＃velismedia": "velismedia.com", "ï¼ƒrubiconproject": "rubiconproject.com", "ï¼ƒpubmatic": "pubmatic.com", "ï¼ƒopenx": "openx.com", "yahoo. com": "yahoo.com", "telariatelaria.com": "telaria.com", "spotx    spotx.tv": "spotx.tv", "spotx    spotxchange.com": "spotx.tv", "smart smartadserver.com": "smartadserver.com", "smart ad server    smartadserver.com": "smartadserver.com", "rubiconrubiconproject.com": "rubiconproject.com", "rubicon.com": "rubiconproject.com", "rubicon rubiconproject.com": "rubiconproject.com", "rubicon    rubiconproject.com": "rubiconproject.com", "revcontentrevcontent.com": "revcontent.com", "reseller admanmedia.com": "admanmedia.com", "pulsepoint    contextweb.com": "contextweb.com", "pulse point - contextweb": "contextweb.com", "pubmatic.comm": "pubmatic.com", "pubmatic pubmatic.com": "pubmatic.com", "pubmatic    pubmatic.com": "pubmatic.com", "prebid rtbhouse.com": "rtbhouse.com", "googlesyndication.com": "google.com", "openx openx.com": "openx.com", "openx    openx.com": "openx.com", "indexexchange.comindexexchange.com": "indexexchange.com", "index indexexchange.com": "indexexchange.com", "index    indexexchange.com": "indexexchange.com", "index.com": "indexexchange.com", "improveddigital.com": "improvedigital.com", "improvedigitalimprovedigital.com": "improvedigital.com", "freewheel freewheel.tv": "freewheel.tv", "freewheel    freewheel.tv": "freewheel.tv", "ebemamae.comgoogle.com": "google.com", "d4c29acad76ce94f outbrain.com": "outbrain.com", "ctwant.com pubmatic.com": "pubmatic.com", "context web.com": "contextweb.com"}
	for mapping in replace_map.keys():
		dom = dom.replace(mapping, replace_map[mapping])
		
	if "." not in dom:
		replace_map = {"adsparc": "adsparc.com", "adsolut": "adsolut.in", "adswizz": "adswizz.com", "aol": "aol.com", "youtube": "youtube.com", "yahoo": "yahoo.com", "xandr": "xandr.com", "waardex": "waardex.com", "ucfunnel": "ucfunnel.com", "spotxchange": "spotxchange.com", "targetspot": "targetspot.com", "spotx.tvspotxchange.com": "spotx.tv", "sovrn": "sovrn.com", "smilewanted": "smilewanted.com", "rubicon": "rubiconproject.com", "revcontent": "revcontent.com", "quantum-advertising": "quantum-advertising.com", "q1connect": "q1connect.com", "pubmatic": "pubmatic.com", "google": "google.com", "taboola": "taboola.com", "spotx": "spotx.tv"}
		for mapping in replace_map.keys():
			dom = dom.replace(mapping, replace_map[mapping])
		
	replace_patterns = ["​", "*.go.", "ï»¿ï»¿", "ï»¿", "...", "34       ", "39  ", "40  ", "41  ", "42  ", "5d62403b186f2ace ", "?", "\\u{200b}", "acd.op.", "appnexus    ", "api.publishers.", " (http://appnexus.com/)", "<http://appnexus.com/>", "beachfront ", "ãƒæ’ã†â€™ãƒâ€ ã¢â‚¬â„¢ãƒæ’ã¢â‚¬ ãƒâ¢ã¢â€šâ¬ã¢â€žâ¢ãƒæ’ã†â€™ãƒâ¢ã¢â€šâ¬ã…â¡ãƒæ’ã¢â‚¬å¡ãƒâ€šã‚â¯ãƒæ’ã†â€™ãƒâ€ ã¢â‚¬â„¢ãƒæ’ã‚â¢ãƒâ¢ã¢â‚¬å¡ã‚â¬ãƒâ€¦ã‚â¡ãƒæ’ã†â€™ãƒâ¢ã¢â€šâ¬ã…â¡ãƒæ’ã¢â‚¬å¡ãƒâ€šã‚â»ãƒæ’ã†â€™ãƒâ€ ã¢â‚¬â„¢ãƒæ’ã‚â¢ãƒâ¢ã¢â‚¬å¡ã‚â¬ãƒâ€¦ã‚â¡ãƒæ’ã†â€™ãƒâ¢ã¢â€šâ¬ã…â¡ãƒæ’ã¢â‚¬å¡ãƒâ€šã‚â¿", "ã¯â»â¿", "ã¢â‚¬â€¹", "â€‹", "â", " (http://yahoo.com/)", " (http://video.unrulymedia.com/)", "verizon media group: ", "verizon marketplace: ", "verizon ", "usa today    ", " [linkprotect.cudasvc.com]", "triplelift ", "tremor - ", "ã", " [link.edgepilot.com] [link.edgepilot.com] [link.edgepilot.com] [link.edgepilot.com]", " (http://synacor.com/)", " [spotxchange.com]", " [spotx.tv]", " (http://sonobi.com/)", " (http://smaato.com/)", " (http://rubiconproject.com/)", " (http://revcontent.com/)", " [openx.com]", "oath - ", "o;?", "newtalk.tw  ", "lkqd    ", "<http://google.com>", " (http://google.com/)", "google adx    ", "fyber - ",  " (http://improvedigital.com/)", "improve    ", "https://www.", "https://", "http://", "/", "www.", "(transfermarkt)", "<http://freewheel.tv>", " (http://emxdgt.com/)", "day:", "<http://contextweb.com>", "cignal        ", "cignal.io        ", "connatix    ", "web: ", "website: www.", "xumo: ",  "xumo lg: ", "unrulyx: ", "sovrn: ", "smaato: ", "pulsepoint: ", "pubmatic: ", "pubmatic apac: ", "pubmatic eu: ", "openx: ", "instream: ", "index exchange: ", "emx digital: ", "dmx: ", "acuity: ", "amazon: ", "brainly s2s amazon: ", "brainly: ", "smartrtb: ", "loopme    "]
	for pattern in replace_patterns:
		dom = dom.replace(pattern, "")

	return_map = {"adcolony.com 496220845654deec reseller 1ad675c9de6b5176": ["adcolony.com", True, "496220845654deec"], "adview.com 58850823 direct": ["adview.com", True, "58850823"], "criteo.com; 9332; direct": ["criteo.com", True, "9332"], "inmobi.com 94d702ada29c4b059e9aca837748b9fc reseller 83e75a7ae333ca9d": ["inmobi.com", True, "94d702ada29c4b059e9aca837748b9fc"], "jeeng.com||1937": ["jeeng.com", True, "1937"], "mars.media 102825": ["mars.media", True, "102825"], "mobilefuse.com 2281 reseller 71e88b065d69c021": ["mobilefuse.com", True, "2281"], "richaudience.com ua8biwjxkr reseller": ["richaudience.co", True, "ua8biwjxkr"], "run-syndicate.com 809": ["run-syndicate.com", True, "809"], "runative-syndicate.com 809": ["runative-syndicate.com", True, "809"], "sharethrough.com 0d60edd5 reseller": ["sharethrough.com", True, "0d60edd5"], "smartyads.com 23": ["smartyads.com", True, "23"], "yldbt.com 5b522cc167f6b300b89dc6d3 reseller cd184cb30abaabb5": ["yldbt.com", True, "5b522cc167f6b300b89dc6d3"], "appnexus": ["appnexus.com", True, "NA"]}
	if dom in return_map.keys():
		return return_map[dom][0], return_map[dom][1], return_map[dom][2]

	if dom in ["adcolony", "adops", "adtag.vidmatic.com", "adtag.vidssp.com", "adyoulke.com", "apnexus.com", "app: aps.amazon.com", "appnexuscom", "bizzclick", "bizzclick.net", "brainly s2s yahoo.com", "ccontextweb.com", "ccoxmt.com", "chinatimes.com indexexchange.com", "cpmstar", "cpubmatic.com", "criteo.net", "dailymotion", "districtm", "districtm: appnexus.com", "eappnexus.com", "emxdgt.com", "emxdigital.com", "emxgdt.com", "emxgt.com", "engageadx", "eplanning.net", "epom", "epom.com", "exponential.com", "exponential.comi", "fmlabsonline", "freestar.io", "freewheel.tv", "freewheel", "go.sonobi.com", "i33across.com", "ijit.com", "index", "indexexchage.com", "indexexchange", "infolinks", "inventorypartnerdomain=failarmy.tv", "inventorypartnerdomain=firstimpression.io", "inventorypartnerdomain=peopleareawesome.tv", "inventorypartnerdomain=thepetcollective.tv", "inventorypartnerdomain=vuit.com", "inventorypartnerdomain=weatherspy.tv", "inventorypartnerdomain=wurl.com", "istrictm.io", "kiwihk", "kqd.com", "kqd.net", "ligit.com", "lijit.copenx.com", "limpid", "magnite", "magnite: rubiconproject.com", "mahimeta", "mapmyfitness liveintent.com", "media-net", "mediaonline.com", "mobfox", "mobupps", "mobuppsrtb.com", "ndexexchange.com", "nsightvideo.com", "o;google.com", "openx", "openx.comm", "openx.net", "outbrain.cbuffom", "penx.com", "pera.media", "potx.tv", "potxchange.com", "ppnexus.com", "publisher.phunware.com", "publishers.adlive.io", "publishers.logicad.jp", "publishers.teads.tv", "pubnative.com", "quantumdx.io", "relaido", "relaido.jp", "rhythmone", "rhythmone.cpm", "rhythomone.com", "riteo.com", "rtbhhouse.com", "rtbhouse", "sekindo", "sharethrough: sharethrough.com", "smartadserver", "sonictwist", "spot.im", "spotexchange.com", "spotim.market", "spotx.com","spotx.tvchange.com", "spotx.tvspotxchange.com", "spotxchange.com", "sulvo.co", "sulvo.com", "syancor.com", "teads.tv", "test.e-planning.net", "themediagrid.com", "themoneytizer.com‚", "tpmn.co.kr", "triplift.com", "viads.co", "video advertising.com", "website: interplaymedia.com.au", "yieldlab.de", "yieldlab.net", "yieldmo", "﻿anyclip.com", "﻿appnexus.com", "﻿google.com", "﻿improvedigital.com", "﻿spotxchange.com", "﻿﻿appnexus.com", "﻿﻿inmobi.com", "﻿﻿rubiconproject.com", "﻿﻿video.unrulymedia.com"]:
		replace_map = {"adcolony": "adcolony.com", "adops": "adops.com", "adtag.": "", "adyoulke.com": "adyoulike.com", "apnexus.com": "appnexus.com", "app: ": "", "appnexuscom": "appnexus.com", "bizzclick": "bizzclick.com", "bizzclick.net": "bizzclick.com", "brainly s2s ": "", "ccontextweb.com": "contextweb.com", "ccoxmt.com": "coxmt.com", "chinatimes.com ": "", "cpmstar": "cpmstar.com", "cpubmatic.com": "pubmatic.com", "criteo.net": "criteo.com", "dailymotion": "dailymotion.com", "districtm": "districtm.io", "districtm: ": "", "eappnexus.com": "appnexus.com", "emxdgt.com": "emxdigital.com", "emxgdt.com": "emxdigital.com", "emxgt.com": "emxdigital.com", "engageadx": "engageadx.com", "epom": "epom.com", "exponential.comi": "exponential.com", "eplanning.net": "e-planning.net", "fmlabsonline": "fmlabsonline.com", "freestar.io": "freestar.com", "freewheel.tv": "freewheel.com", "freewheel": "freewheel.com", "go.sonobi.com": "sonobi.com", "i33across.com": "33across.com", "ijit.com": "lijit.com", "index": "indexexchange.com", "indexexchage.com": "indexexchange.com", "indexexchange": "indexexchange.com", "infolinks": "infolinks.com", "inventorypartnerdomain=": "", "istrictm.io": "districtm.io", "kiwihk": "kiwihk.net", "kqd.com": "lkqd.com", "kqd.net": "lkqd.net", "ligit.com": "lijit.com", "lijit.copenx.com": "openx.com", "limpid": "limpid.tv", "magnite: ": "", "mahimeta": "mahimeta.com", "mapmyfitness ": "", "media-net": "media.net", "mediaonline.com": "9mediaonline.com", "mobfox": "mobfox.com", "mobupps": "mobupps.com", "mobuppsrtb.com": "mobupps.com", "ndexexchange.com": "indexexchange.com", "o;google.com": "google.com", "openx": "openx.com", "openx.comm": "openx.com", "openx.net": "openx.com", "outbrain.cbuffo": "outbrain.com", "penx.com": "openx.com", "pera.media": "opera.com", "potx.tv": "spotx.tv", "potxchange.com": "spotx.tv", "ppnexus.com": "appnexus.com", "publisher.": "", "publishers.": "", "pubnative.com": "pubnative.net", "quantumdx.io": "quantumdex.io", "relaido": "relaido.jp", "rhythmone": "rhythmone.com", "rhythmone.cpm": "rhythmone.com", "rhythomone.com": "rhythmone.com", "riteo.com": "criteo.com", "rtbhouse": "rtbhouse.com", "rtbhhouse.com": "rtbhouse.com", "sekindo": "sekindo.com", "sharethrough: ": "", "smartadserver": "smartadserver.com", "sonictwist": "sonictwist.media", "spotexchange.com": "spotx.tv", "spotx.com": "spotx.tv", "spotx.tvchange.com": "spotx.tv", "spotx.tvspotxchange.com": "spotx.tv", "spotxchange.com": "spotx.tv", "sulvo.co": "sulvo.com", "syancor.com": "synacor.com", "teads.tv": "teads.com", "spot.im": "spotim.market", "test.e-planning.net": "e-planning.net", "themoneytizer.com‚": "themoneytizer.com", "tpmn.co.kr": "tpmn.io", "triplift.com": "triplelift.com", "viads.co": "viads.com", "video ": "", "weborama.nl": "", "website: ": "", "yieldlab.de": "yieldlab.com", "yieldlab.net": "yieldlab.com", "yieldmo": "yieldmo.com", "﻿": ""}
		for mapping in replace_map.keys():
			dom = dom.replace(mapping, replace_map[mapping])

	return dom, True, "NA"



def get_pool_owner_domain(ad_domain, seller_id):
	'''
	Function to retrieve the owner domain of the current seller_id in the network of the current ad_domain
	'''

	global sellersjson_directory;

	# File name of the sellers.json file of the current ad_domain
	filename = str(sellersjson_directory) + "/" + str(ad_domain).replace(".","_") + ".json"
		
	# Opening the sellers.json file for current ad_domain. 
	# If sellers.json does not exist, then return "sellersjson_not_available"
	try:
		f = open(filename)
	except BaseException as e:
		return "sellersjson_not_available"

	ad_sellers = {}
	seller_domain = ""

	# Parse google's sellers.json differently than others
	try:
		if ad_domain in ["google.com"]:
			ad_sellers = json.loads(ast.literal_eval(json.dumps(f.read())))
		else:
			json_string = json.load(f)
			ad_sellers = json.loads(json_string)
	except json.JSONDecodeError as e:
		try:
			if json_string != "":
				# Correcting some incorrect syntax of JSON
				json_string.replace(" ","").replace("\n","").replace("\t","").replace(",]","]").replace(",}","}").strip(",")
				ad_sellers = json.loads(json_string)
		except:
			return "sellersjson_not_available"

	# Traverse through each entry of the sellers.json
	try:
		for seller in ad_sellers["sellers"]:
			sid, is_confidential, seller_domain = "NA", "False", "unused_seller_id"

			# If key: "seller_id" exists in the sellers.json entry and matched the currently passed seller_id to the function then do the following
			if "seller_id" in seller.keys():
				sid = str(seller["seller_id"]).strip().lower()
				if sid == seller_id:
					
					# If current entry is confidential, then return "confidential_seller" as the owner_domain
					# If the key "domain" is absent in the current sellers.json entry, then return "not available" as the owner domain
					# Else, if the domain is present, return the domain as the owner domain
					if "is_confidential" in seller.keys():
						if seller["is_confidential"] == 1:
							is_confidential = "True"
							seller_domain = "confidential_seller"
						else:
							if "domain" in seller.keys():
								seller_domain = str(seller["domain"]).replace("https://","").replace("http://","").replace("www.","").strip().lower()
							else:
								seller_domain = "not_available"
					else:
						if "domain" in seller.keys():
							seller_domain = str(seller["domain"]).replace("https://","").replace("http://","").replace("www.","").strip().lower()
						else:
							seller_domain = "not_available"
					break;
	except:
		return "sellersjson_not_available"
	
	# Performing some processing before returning the seller_domain as the owner domain
	seller_domain = seller_domain.replace("​", "").replace("/", "").replace("aps.amazon.comapsindex.html", "aps.amazon.com").replace("disqus", "disqus.com").replace("mediavine.comsellers.json", "mediavine.com").replace("aps.amazon.comapsunified-ad-marketplace", "aps.amazon.com")
	return seller_domain
						


def parse_adstxt(ad_sellers):
	'''
	Parses the ads.txt
	'''
	all_sellers = []
	
	for seller in ad_sellers:
		
		# item_list stores different information about a seller
		item_list = []
		s = seller
		
		# Character "#" is used to denote comment in ads.txt. So, text after "#" is ignored
		if "#" in seller:
			s = seller[:seller.index("#")]

		# Ignoring garbage which is too short to represent any valid seller
		if len(s) < 5:
			continue
		else:
			# Obtain different components of an ads.txt entry (which are separated by a ",")
			temp = s.split(",")
			
			# Strip any empty spaces in front and last and convert current "ad_domain" to lower case
			item_list.append(temp[0].strip().lower())
			
			if len(temp) >= 2:
				if temp[1].strip() == "":
					item_list.append("NA")
				else:
					# Extract and append current "seller_id"
					item_list.append(temp[1].strip().lower())

				if len(temp) >= 3:
					if temp[2].strip() == "":
						item_list.append("NA")
					else:
						# Extract and append current "seller_account_type"
						item_list.append(temp[2].strip().upper())

					if len(temp) >= 4:
						if temp[3].strip() == "":
							item_list.append("NA")
						else:
							# Extract and append current "certification_authority_id"
							item_list.append(temp[3].strip())
					else:
						item_list.append("NA")
				else:
					item_list.append("NA")
					item_list.append("NA")
			else:
				item_list.append("NA")
				item_list.append("NA")
				item_list.append("NA")
			
			all_sellers.append(item_list)

	return all_sellers



def check_reseller_relationship(adom, sid):
	'''
	Checks RESELLER Relationship
	'''
	global dfs;

	l = dfs[(dfs["ad_domain"] == adom)]["seller_id"].unique().tolist()
	return_value = True if sid in l else False
	return return_value



def extract_pooling_from_study_domains():
	'''
	Extracts the "ad_domain|seller_id" string pairs from ads.txt of study domains.
	These string keys could be shared by other domains for pooling.
	'''
	global study_domains, all_domains, static_pools;

	for i in range(len(dfa)):
			
		domain = str(dfa.iloc[i]["website_domain"]).strip().lower().replace("https://","").replace("http://","").replace("www.","")
		print(i, domain)
		
		# Process the ad domain and ignore the current row if it is invalid (i.e., False is returned)
		ad_domain, flag, sid = process_ad_domain(str(dfa.iloc[i]["ad_domain"]))
		if flag == False:
			continue

		if sid != "NA":
			seller_id = sid
		else:
			# Process the seller_id and ignore the current row if it is invalid (i.e., False is returned)
			seller_id, flag = process_seller_id(str(dfa.iloc[i]["seller_id"]))
			if flag == False:
				continue

		if domain not in study_domains:
			study_domains.append(domain)
			all_domains.append(domain)

		adstxt_presence = str(dfa.iloc[i]["adstxt_presence"])
		if adstxt_presence == "Yes":
			seller_type = str(dfa.iloc[i]["seller_account_type"])
			pool_str = ad_domain + "|" + seller_id
			domain_str = domain + "|S"

			# If the ad_domain is mentioned as "RESELLER" in ads.txt and 
			# If it is also a valid "INTERMEDIARY"/"BOTH" in corresponding sellers.json entry, then its not dark pooling
			check_flag = False
			if seller_type == "RESELLER":
				check_flag = check_reseller_relationship(ad_domain, seller_id)
			if check_flag == True:
				continue

			if pool_str not in static_pools.keys():
				static_pools[pool_str] = {"StudyPool": []}
			static_pools[pool_str]["StudyPool"].append(domain_str)

	print("ads.txt of domains under study analysed for potential pooling.")
	return



def discover_pools_in_100k_domains():
	'''
	Function to discover all the static pools of study domains amongst the top 100K Tranco domains
	'''
	global top100k_adstxt_directory, study_domains, all_domains;

	for file in os.listdir(top100k_adstxt_directory):
		print(os.listdir(top100k_adstxt_directory).index(file), file)

		if ".DS_Store" in file:
			continue
		
		top_100k_domain = str(file).replace("_",".").replace(".txt","").strip().lower()
		if top_100k_domain in study_domains:
			continue
		domain_str = top_100k_domain + "|O"
		
		f = open(top100k_adstxt_directory + "/" + str(file), "r")
		adstxt_lines = f.read().split("\n")
		adstxt_sellers = parse_adstxt(adstxt_lines)

		for seller in adstxt_sellers:

			# Process the ad domain and ignore the current row if it is invalid (i.e., False is returned)
			ad_domain, flag, sid = process_ad_domain(str(seller[0]))
			if flag == False:
				continue

			if sid != "NA":
				seller_id = sid
			else:
				# Process the seller_id and ignore the current row if it is invalid (i.e., False is returned)
				seller_id, flag = process_seller_id(str(seller[1]))
				if flag == False:
					continue

			seller_type = str(seller[0]).upper()
			check_flag = False
			if seller_type == "RESELLER":
				check_flag = check_reseller_relationship(ad_domain, seller_id)
			if check_flag == True:
				continue

			if top_100k_domain not in all_domains:
				all_domains.append(top_100k_domain)

			pool_str = ad_domain + "|" + seller_id
			if pool_str in static_pools.keys():
				if "StudyPool" in static_pools[pool_str].keys():
					static_pools[pool_str]["StudyPool"].append(domain_str)
				elif "OtherPool" in static_pools[pool_str].keys():
					static_pools[pool_str]["OtherPool"].append(domain_str)
			elif pool_str not in static_pools.keys():
				static_pools[pool_str] = {"OtherPool": []}
				static_pools[pool_str]["OtherPool"].append(domain_str)

	return



def discover_parents():
	'''
	Discover parent organizations of all the domains using DuckDuckGo (DDG) Entity-Organization list
	'''
	global entity_dir, all_domains, domain_to_parent_map;

	for file in os.listdir(entity_dir):
		
		if file == ".DS_Store":
			continue
		
		curr_file = os.path.join(entity_dir, file)
		json_file = open(curr_file)
		data_dict = json.load(json_file)
		parent = str(data_dict["name"])
		sites = data_dict["properties"]

		for site in sites:
			if site in all_domains:
				if site not in domain_to_parent_map.keys():
					domain_to_parent_map[site] = parent

	return



def most_frequent(list_):
	'''
	Function to compute the most frequent item in the list, % of occurence of that item
	This function is used for computing most frequent/common parent of pooled domains and % of domains that share that same parent
	'''
	if len(list_) == 0:
		return "NA", "NA"
	occurence_count = Counter(list_)
	most_freq = occurence_count.most_common(1)[0][0]
	freq = occurence_count.most_common(1)[0][1]
	return most_freq, round((freq/len(list_))*100,2)



def get_pool_classification(parents, domains_sharing_pool):
	'''
	Function to obtain the parent based classification of the pool
	'''

	if len(parents) == 0:
		# No information about parent available in DDG for any of the pooled domains in this pool 
		pool_classification = "incomplete_parent_information"
	
	elif len(parents) == len(domains_sharing_pool.split("; ")):
		# Information about the parent of all the domains is available
		if len(list(set(parents))) == 1:
			pool_classification = "homogenous"
		else:
			pool_classification = "heterogenous"
	
	else:
		# Information about the parent of all the domains being pooled is not available
		if len(list(set(parents))) == 1:
			# With whatever information that is available, the pooled domains seem to have the same parent
			pool_classification = "incomplete_homogenous"
		else:
			pool_classification = "heterogenous"

	return pool_classification



def main():

	global domain_to_parent_map;

	# Creating and opening the csv file for saving the static pools
	pool_directory, static_pool_filename = "", "static_pools.csv"
	static_pool_filepath = os.path.join(pool_directory, static_pool_filename)
	f_csv = open(static_pool_filepath, 'w', encoding='UTF8')
	writer = csv.writer(f_csv)

	# Defining and writing header to the csv file
	header_str = "pool_type, parents, distinct_parent_count, most_common_parent, percent_domains_sharing_the_most_common_parent, pool_classification, ad_domain, seller_id, ad_domain|seller_id, pool_owner_domain, pool_size, domains_sharing_pool"
	header = header_str.split(", ")
	writer.writerow(header)

	# Extract ad_domain|seller_id strings from study domains which have potential of being pooled
	extract_pooling_from_study_domains()

	# Extract ad_domain|seller_id strings from top 100K domains to show pooling of study domains
	discover_pools_in_100k_domains()
	

	# Discover mapping of domains to parents as per the DuckDuckGo Entity-Organization list
	discover_parents()

	# Extracting additional parent details and pool classification of each pool and writing pool details to a csv file
	for pool in static_pools.keys():

		row = []

		pool_type = str(list(static_pools[pool].keys())[0])
		pool_size = len(list(set(static_pools[pool][pool_type])))
		if pool_size <= 1:
			continue
		ad_domain = str(pool.split("|")[0].lower())
		seller_id = str(pool.split("|")[1].lower())
		owner_domain = get_pool_owner_domain(ad_domain, seller_id)
		domains_sharing_pool = "; ".join(list(set(static_pools[pool][pool_type])))
		parents_of_current_domains = [domain_to_parent_map[dom.split("|")[0]] for dom in domains_sharing_pool.split("; ") if dom.split("|")[0] in domain_to_parent_map.keys()]
		most_frequent_parent, freq_parent_coverage = most_frequent(parents_of_current_domains)
		pool_classification = get_pool_classification(parents_of_current_domains, domains_sharing_pool)

		if pool_classification == "incomplete_parent_information":
			parents_of_current_domains = ["NA"]

		parents = "; ".join(list(set(parents_of_current_domains)))
		distinct_parent_count = len(list(set(parents_of_current_domains))) if parents != "NA" else "NA"

		row.append(pool_type)
		row.append(parents)
		row.append(distinct_parent_count)
		row.append(most_frequent_parent)
		row.append(freq_parent_coverage)
		row.append(pool_classification)
		row.append(ad_domain)
		row.append(seller_id)
		row.append(pool)
		row.append(owner_domain)
		row.append(pool_size)
		row.append(domains_sharing_pool)

		writer.writerow(row)

	return


if __name__ == "__main__":
	main()