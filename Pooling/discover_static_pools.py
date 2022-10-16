import pandas as pd
import json
import csv
import ast
import os
import re



# df = pd.read_csv("summary_misinfo_adstxt.csv")
df = pd.read_csv("summary_control_adstxt.csv")
dfs = pd.read_csv("subset_sellersjson_m_intermediary.csv", quotechar="\"")
# dfs = pd.read_csv("summary_sellersjson_m.csv")

dark_pools = {}

adstxt_dir = "./adstxt"
sellersjson_dir = "./sellersjson"

misinformation_domains = []





def process_seller_id(sellerid):

	# Set of values in "seller_id" field that are incorrect/invalid
	incorrect_seller_id_values = ["pub_team_insert_pub_id_here", "id", "website id/publisher id", "supplyid", "xxxxxx", "abc%20local", "bauer%20media", "beliefnet", "big%20news%20site%201", "cbs%20local", "coedmedia", "entercom", "evolve%20media", "frankly", "horoscope.com", "hubbard%20radio", "merriam-webster", "prebid%20-%20pbh%20network", "prebid%20-%20smediavine", "purch", "usa%20today%20sports", "vox%20media", "wral", "aakljaan", "evfn2aah", "xxxx5", "xxxxxxxxxxx", "admin", "vk.vom", "your unique ads.txt id", "aca va el channel id", "nan", "reseller", "direct", "insert_your_vi_publisher_id_here", "reseller", "publisher id", "pui", "test.e-planning.", "badgirl", "spacedaily@gmail.com", "xxx", "xxx", "insert_udm_pid_here", "xxxxxxxxxxxxxxxxxxxx", "ahn3axrjaa==-a123", "ahn3axrjaa==-a14", "ahn3axrjaa==-a23", "ahn3axrjaa==-a61", "ahn3axrjaa==-a74", "q3n3axrjaa==-a162", "q3n3axrjaa==-a168", "q3n3axrjaa==-a184", "qnn3axrjaa==-a136", "qnn3axrjaa==-a141", "qnn3axrjaa==-a144", "rhn3axrjaa==-a144", "reseller", "nan", "switchconceptopenrtb", "xxxxxxxx", "backstage.pubid", "reseller", "switchconcepts", "pbn", "inr", "smt", "xxxxxx", "undefined", "xxxx-xxxx-01", "xxxx-xxxx-xx", "xxxxxxxxxx", "sell", "pubmatic.com", "pubid", "xxxxxx", "25ans_wedding_3_4", "media_id", "bali.idntimes.com", "banten.idntimes.com", "buzzfeed_amp", "buzzfeed_text_amp", "camphack.nap-camp.com", "cyclehack.jp", "duniaku.idntimes.com", "ejje.weblio.jp", "ejje.weblio.jp_amp", "elle_b_3_4", "ellegirl.jp_34", "harpersbazaar_jp_3_4", "jabar.idntimes.com", "jateng.idntimes.com", "jatim.idntimes.com", "jogja.idntimes.com", "kaltim.idntimes.com", "lampung.idntimes.com", "news.nifty.com", "nifty", "nifty_amp", "nifty_sdk", "ntb.idntimes.com", "runhack.jp", "sulsel.idntimes.com", "sumsel.idntimes.com", "sumut.idntimes.com", "thesaurus.weblio.jp_amp", "translate.weblio.jp", "tsurihack.com", "www.25ans.jp_3_4", "www.buzzfeed.com", "www.cosmopolitan.com_jp_3_4", "www.cosmopolitan.com_jp_amp_3_4", "www.esquire.com_3_4", "www.fujingaho.jp_3_4", "www.idntimes.com", "www.nifty.com", "www.popbela.com", "www.popmama.com", "www.womenshealthmag.com_3_4", "yamahack.com", "domainid", "xxxxx", "direct", "account id", "your_account_id", "your_site_id", "placeholder", "direct", "openx id", "reseller", "your_account_id", "omg zero", "mannenmedia", "ster", "weborama", "xxxx", "reseller", "aol.com", "nan", "your_publisher_id", "direct", "7xxxxx", "direct", "adwaveus", "atunwa", "audacy", "audioemotion", "audioone", "audioxi", "bauermedia", "cox", "coxmediagroup", "cumulus", "di", "entercom", "entravision", "hcode", "iheartmedia", "kriteria", "leanstreamdemand", "linkfire", "nextregie", "octave", "otherwortb", "pandora", "podiumaudio", "qmusic", "remixd", "rogers", "rpp", "sbs", "soundcloud", "speechkit", "talksport", "targetspot", "townsq", "trinityaudio", "tunein", "univision", "videobyte", "washingtonpost", "dax", "trinityaudio", "nan", "insert your uam pub id found here", "pub id", "nan", "switchconcepts", "your publisher id", "compass pub id", "number", "eduard", "reseller", "15xxxx", "seller_id", "spot_id", "direct", "direct", "direct", "*lkqdaccount*", "xxxxxx", "client uuid", "clientuuid", "****", "anuntis-es", "csnstores", "direct", "google.com", "lmc-digitalfirstmedia", "mobile-softoniccom", "olx-ua", "pub-", "reseller", "softonic", "tablet-softoniccom", "reseller", "quinstreet", "dmg", "&", "waytogrow/dominik.czarnota@waytogrow.eu", "waytogrow/janusz.michalik@waytogrow.pl", "switch", "direct", "reseller", "reseller", "____", "*publisher-id*", "pub 2320327466016366) -eb", "&lt;148395&gt;"]

	tidd = sellerid.strip().lower().strip("\"")
	tidd = tidd.strip().strip(" ").strip("[").strip("]").strip("{{").strip("}}").strip("{").strip("}").strip("(").strip(")").strip("<").strip(">").strip().strip(" ")

	if tidd in incorrect_seller_id_values:
		return "", False

	tidd = tidd.replace("\\capub-", "pub-").replace("ca-games-pub-", "pub-").replace("ca-mb-app-pub-", "pub-").replace("ca-pub-", "pub-")
	tidd = tidd.replace("mb-app-pub-", "pub-").replace("ca-video-pub-", "pub-").replace("dis841569", "841569").replace("video-pub-", "pub-")
	tidd = tidd.replace("partner-pub-", "pub-").replace("pub- ", "pub-").replace("pub7249223325809944", "pub-7249223325809944").replace("pub-pub-", "pub-")
	tidd = tidd.replace("ub-1283624027922691", "pub-1283624027922691").replace("b- 059922", "b-059922")

	replace_patterns = ["​", "â  ", "â ", "ã‚â ", "ăâ ", "directâ ", "resellerâ ", "â ", "آ ", 
						"р  рір‚в„ў ", "ãƒâ€š ", "â ", "ã‚ ", "ãš ", " direct", "direct", "client ", "ξβξβ ", "ξ ", 
						"ãš", "ãƒâ€šã‚â ", "1 ", "â€‹", "?", "tl ", "reseller", "*"]
	for pattern in replace_patterns:
		tidd = tidd.replace(pattern, "")

	tidd = tidd.replace("ma6m9pbvib, , 1363", "1363").replace("publisher_ 5171", "publisher_5171").replace("|1937|", "1937").replace("â¬â€ 440647", "440647")
	tidd = tidd.replace("ãƒâ€šã‚18222", "18222").replace("ã‚74d964d64622eda353dbb95047d88f16", "74d964d64622eda353dbb95047d88f16").replace("ã‚aab3b5904a4f1c27f53084dbb14945a1", "aab3b5904a4f1c27f53084dbb14945a1")
	tidd = tidd.replace("ã‚f15f921e8523dda73e32ff2a6069788f", "f15f921e8523dda73e32ff2a6069788f").replace("ã‚f963243b8472aa9474d37bb6173c4f18", "f963243b8472aa9474d37bb6173c4f18")
	tidd = tidd.replace("ă196713", "196713").replace("ă50", "50").replace("ăb-060443", "b-060443")


	if tidd in ["pid", "property code", "publisher_id", "publisherid", "purch.com"]:
		return "", False

	return tidd, True




def process_ad_domain(domain_str):

	incorrect_domain_values = ["ads.txt", "video", "video:", "video.", "video demand partners:", "vertamedia certification authority id - 7de89dc7742b5b11.", "verizon", "verizon/aol","usa today", "twitter", "test ads.txt", "terms of use", "terms and conditions", "termina", "telaria", "telaria.cyahoom", "teads", "t2est ads.txt", "support", "sticky ads (open marketplace) = freewheel", "sticky ads (deal)  - freewheel", "startapp.com smt reseller", "skip to content", "search", "rubicon ads.txt", "resources", "reseller", "quick links", "purch.com", "publishers", "privacy policy", "pricing", "press", "posumeads.com & pocketmath.com","portail orange", "portail orange reunion", "policies", "playground xyz", "partners", "optional reseller lines", "optional lines:", "opsco", "only include taboola for techcrunch & engadget", "ona for media services - adx emea", "oath", "netlink banner: adx partner", "nativo", "native demand partners:", "mowplayer", "linkedin", "google adsense", "home", "invoices", "inbox", "insticator", "features", "facebook.com", "eseller", "entry", "egami", "display", "disallow:", "direct", "daria", "cookies","contact", "contact: adops@interplaymedia.com.au", "contact us", "concat", "company", "cloud", "close", "checkout", "case studies", "careers", "calendar", "brightcom vdx", "bingo pop line items:", "search", "pub-2205121062140812", "pub-2603664881560000", "pub-2726428685015992", "pub-3132893725603935", "pub-7913044002918072", "pub-7915887679464005", "16189", "17250", "3563", "18 13132", "1813132", "1992", "22069", "22069", "256757", "458", "4ad745ead2958bf7", "560382", "59491", "60d26397ec060f98", "6796094", "6c8d5f95897a5a3b", "72av8h", "75547ba18f13f74", "7de89dc7742b5b11", "80media", "83e75a7ae333ca9d", "a14650a2-7db0-4d21-9666-4b1b9b32aa08", "a670c89d4a324e47", "f08c47fec0942fa0 lkqd.net", "f08c47fec0942fa0", "fcadx-55297863", "1371890", ".com", "ca-pub-8787923930478618", "ca-video-pub-8787923930478618", "0bfd66d529a55807", "smartx"]
	dom = domain_str.strip().lower().strip("\"")

	id_mappings = {"exponential.com	176430direct	afac06385c445926": ["exponential.com", "176430"], "google.comâ pub-491005001790614": ["google.com", "pub-491005001790614"], "google.comâ pub-491005001790614": ["google.com", "pub-491005001790614"], "aps.amazon.com 3854 reseller": ["aps.amazon", "3854"], "136839spotx.tv": ["spotx.tv", "136839"], "xad.com 241 reseller 81cbf0a75a5e0e9a": ["xad.com", "241"], "widespace.com - 8470 - direct": ["widespace.com", "8470"], "widespace.com - 8471 - direct": ["widespace.com", "8471"], "tsyndicate.com 32164": ["tsyndicate.com", "32164"], "tsyndicate.com 32207": ["tsyndicate.com", "32207"], "sonobi.com b24c93d5b8 direct": ["sonobi.com", "b24c93d5b8"], "smartadserver.com 3117 reseller": ["smartadserver.com", "3117"], "smartadserver.com 3668 reseller": ["smartadserver.com", "3668"], "sekindo.com 19327  direct": ["sekindo.com", "19327"], "rubiconproject.com 16824 reseller 0bfd66d529a55807": ["rubiconproject.com", "16824"], "rhythmone.com 1059622079 reseller": ["rhythmone.com", "1059622079"], "rhythmone.com 4201299756 reseller a670c89d4a324e47": ["rhythmone.com", "4201299756"], "roqoon.com 134034 reseller": ["roqoon.com", "134034"], "pokkt.com 5886 reseller c45702d9311e25fd": ["pokkt.com", "5886"], "openx.com 537106719 reseller 6a698e2ec38604c6": ["openx.com", "537106719"], "openx.com 537126269 reseller": ["openx.com", "537126269"], "openx.com 537149762 reseller 6a698e2ec38604c6": ["openx.com", "537149762"], "openx.com 540191398 reseller 6a698e2ec38604c6": ["openx.com", "540191398"], "openx.com 540421297 reseller 6a698e2ec38604c6": ["openx.com", "540421297"], "openx.com 540634022 reseller 6a698e2ec38604c6": ["openx.com", "540634022"], "openx.com537126269reseller": ["openx.com", "537126269"], "lockerdome.com12038519593865728direct": ["lockerdome.com", "12038519593865728"], "lkqd.com 423 reseller 59c49fa9598a0117": ["lkqd.com", "423"], "lijit.com 215294 reseller fafdf38b16bf6b2b": ["lijit.com", "215294"], "lijit.com 215294-eb reseller fafdf38b16bf6b2b": ["lijit.com", "215294-eb"], "indexexchange.com 184110 reseller": ["indexexchange.com", "184110"], "indexexchange.com 184270 reseller 50b1c356f2c5c8fc": ["indexexchange.com", "184270"], "indexexchange.com184110reseller": ["indexexchange.com", "184110"], "improvedigital.com 1129 reseller": ["improvedigital.com", "1129"], "improvedigital.com 1175 reseller": ["improvedigital.com", "1175"], "improvedigital.com 1225	reseller": ["improvedigital.com", "1225"], "improvedigital.com 1227	reseller": ["improvedigital.com", "1227"], "improvedigital.com 1267	reseller": ["improvedigital.com", "1267"], "gumgum.com 13244 direct ffdef49475d318a9": ["gumgum.com", "13244"], "google.com pub-4588688220746183 direct 5338762016": ["google.com", "pub-4588688220746183"], "google.com-pub": ["google.com", "pub-3805568091292313"], "freewheel.tv 1069 reseller": ["freewheel.tv", "1069"], "freewheel.tv 1076753 reseller": ["freewheel.tv", "1076753"], "freewheel.tv 1076769 reseller": ["freewheel.tv", "1076769"], "freewheel.tv 1091073 reseller": ["freewheel.tv", "1091073"], "freewheel.tv 1091089 reseller": ["freewheel.tv", "1091089"], "freewheel.tv 133681 reseller": ["freewheel.tv", "133681"], "freewheel.tv 133777 reseller": ["freewheel.tv", "133777"], "freewheel.tv 156113 reseller": ["freewheel.tv", "156113"], "freewheel.tv 1867 reseller": ["freewheel.tv", "1867"], "freewheel.tv 1873 reseller": ["freewheel.tv", "1873"], "freewheel.tv 1929 reseller": ["freewheel.tv", "1929"], "freewheel.tv 1931 reseller": ["freewheel.tv", "1931"], "freewheel.tv 1933 reseller": ["freewheel.tv", "1933"], "freewheel.tv 1937 reseller": ["freewheel.tv", "1937"], "freewheel.tv 5649 reseller": ["freewheel.tv", "5649"], "freewheel.tv 654226 reseller": ["freewheel.tv", "654226"], "freewheel.tv 654242 reseller": ["freewheel.tv", "654242"], "freewheel.tv 985441 reseller": ["freewheel.tv", "985441"], "freewheel.tv 985473 reseller": ["freewheel.tv", "985473"], "districtm.io 100962 reseller": ["districtm.io", "100962"], "engagebdr.com 16 reseller": ["engagebdr.com", "16"], "coxmt.com 2000067997102 reseller": ["coxmt.com", "2000067997102"], "coxmt.com 2000068024302 direct": ["coxmt.com", "2000068024302"], "coxmt.com2000067997102reseller": ["coxmt.com", "2000067997102"], "contextweb.com 560606 reseller": ["contextweb.com", "560606"], "contextweb.com 561481 reseller": ["contextweb.com", "561481"], "contextweb.com 561562 reseller 89ff185a4c4e857": ["contextweb.com", "561562"], "c1exchange.com c1x201401 reseller": ["c1exchange.com", "c1x201401"], "c1exchange.com c1x_a9_uampubs reseller": ["c1exchange.com", "c1x_a9_uampubs"], "174835 – direct – criteo.com": ["criteo.com", "174835"], "admanmedia.com 552 reseller": ["admanmedia.com", "552"], "adtech.com 10861 reseller": ["adtech.com", "10861"], "adtech.com 4687 reseller": ["adtech.com", "4687"], "aol.com	27093 reseller": ["aol.com", "27093"], "aol.com	46658 reseller": ["aol.com", "46658"], "aolcloud.net 10861 reseller": ["aolcloud.net", "10861"], "aolcloud.net 4687 reseller": ["aolcloud.net", "4687"], "advertising.com 22153 reseller": ["advertising.com", "22153"], "advertising.com 7574 reseller": ["advertising.com", "7574"], "appnexus.com 1908 reseller f5ab79cb980f11d1": ["appnexus.com", "1908"], "appnexus.com 2928 reseller": ["appnexus.com", "2928"], "appnexus.com 7944 reseller": ["appnexus.com", "7944"], "appnexus.com 8233 reseller": ["appnexus.com", "8233"], "bidmachine.io 36 reseller": ["bidmachine.io", "36"], "bidmachine.io 60 reseller": ["bidmachine.io", "60"], "pubmatic.com 120391 reseller 5d62403b186f2ace": ["pubmatic.com", "120391"], "pubmatic.com 156138 reseller": ["pubmatic.com", "156138"], "pubmatic.com 156248 reseller": ["pubmatic.com", "156248"], "pubmatic.com 156556 reseller": ["pubmatic.com", "156556"], "pubmatic.com 157150 reseller 5d62403b186f2ace": ["pubmatic.com", "157150"], "pubmatic.com 157743": ["pubmatic.com", "157743"], "pubmatic.com156138reseller": ["pubmatic.com", "156138"], "pubmatic.com156248reseller": ["pubmatic.com", "156248"], "pubmatic.com156556reseller": ["pubmatic.com", "156556"], "video.unrulymedia.com 1237114149": ["video.unrulymedia.com", "1237114149"], "rhythmone.com1683053691": ["rhythmone.com", "1683053691"], "pmp.adcrew.co  89ff185a4c4e857c": ["pmp.adcrew.co", "89ff185a4c4e857c"], "openx.com 540731760": ["openx.com", "540731760"], "increaserev.com 234233": ["increaserev.com", "234233"], "increaserev.com 234234": ["increaserev.com", "234234"], "increaserev.com 242412": ["increaserev.com", "242412"], "aol.com 57683": ["aol.com", "57683"],"appnexus.com/564": ["appnexus.com", "564"], "yahoo.com 58578": ["yahoo.com", "58578"], "spotxchange.com 249286": ["spotxchange.com", "249286"], "spotx.tv 108933": ["spotx.tv", "108933"], "spotx.tv 249286": ["spotx.tv", "249286"], "smartadserver.com 3050": ["smartadserver.com", "3050"], "rubiconproject.com 11560": ["rubiconproject.com", "11560"], "rubiconproject.com 17280": ["rubiconproject.com", "17280"], "rhythmone.com1683053691": ["rhythmone.com", "1683053691"], "openx.com 537149888": ["openx.com", "537149888"], "marsmedia. 102825": ["mars.media 102825", "102825"], "indexexchange.com 191730": ["indexexchange.com", "191730"], "indexexchange.com194527": ["indexexchange.com", "194527"], "improvedigital.com 1680": ["improvedigital.com", "1680"], "gothamads.com 126": ["gothamads.com", "126"], "gothamads.com126": ["gothamads.com", "126"], "google.com pub-4299156005397946": ["google.com", "pub-4299156005397946"], "google.com pub-7079691902491759": ["google.com", "pub-7079691902491759"], "districtm.io 100962": ["districtm.io", "100962"], "districtm.io 101760": ["districtm.io", "101760"], "emxdgt.com 1759": ["emxdgt.com", "1759"], "contextweb.com 560288": ["contextweb.com", "560288"], "adform.com 1889": ["adform.com", "1889"], "airpush.com 292001": ["airpush.com", "292001"], "aol.com	21364": ["aol.com", "21364"], "aol.com 58578": ["aol.com", "58578"], "advertising.com 29034": ["advertising.com", "29034"], "adyoulike.com 83d15ef72d387a1e60e5a1399a2b0c03": ["adyoulike.com", "83d15ef72d387a1e60e5a1399a2b0c03"], "appnexus.com 1019": ["appnexus.com", "1019"], "appnexus.com 1314": ["appnexus.com", "1314"], "appnexus.com 4009": ["appnexus.com", "4009"], "pubmatic.com 156078": ["pubmatic.com", "156078"], "pubmatic.com156631": ["pubmatic.com", "156631"],}
	if dom in id_mappings.keys():
		return id_mappings[dom][0], True, id_mappings[dom][1]

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


	dom = dom.replace("nsticator.com", "insticator.com").replace("a.twiago.com", "twiago.com").replace("ads-9dots.project-limelight.com/sellers.json", "project-limelight.com").replace("ads.9dots.project-limelight.com/sellers.json", "project-limelight.com")
	dom = dom.replace("＃velismedia", "velismedia.com").replace("ï¼ƒrubiconproject", "rubiconproject.com").replace("ï¼ƒpubmatic", "pubmatic.com").replace("ï¼ƒopenx", "openx.com").replace("yahoo. com", "yahoo.com")
	dom = dom.replace("telariatelaria.com", "telaria.com").replace("spotx    spotx.tv", "spotx.tv").replace("spotx    spotxchange.com", "spotx.tv").replace("smart smartadserver.com", "smartadserver.com")
	dom = dom.replace("smart ad server    smartadserver.com", "smartadserver.com").replace("rubiconrubiconproject.com", "rubiconproject.com").replace("rubicon.com", "rubiconproject.com").replace("rubicon rubiconproject.com", "rubiconproject.com").replace("rubicon    rubiconproject.com", "rubiconproject.com")
	dom = dom.replace("revcontentrevcontent.com", "revcontent.com").replace("reseller admanmedia.com", "admanmedia.com").replace("pulsepoint    contextweb.com", "contextweb.com").replace("pulse point - contextweb", "contextweb.com")
	dom = dom.replace("pubmatic.comm", "pubmatic.com").replace("pubmatic pubmatic.com", "pubmatic.com").replace("pubmatic    pubmatic.com", "pubmatic.com").replace("prebid rtbhouse.com", "rtbhouse.com").replace("googlesyndication.com", "google.com")
	dom = dom.replace("openx openx.com", "openx.com").replace("openx    openx.com", "openx.com").replace("indexexchange.comindexexchange.com", "indexexchange.com").replace("index indexexchange.com", "indexexchange.com").replace("index    indexexchange.com", "indexexchange.com").replace("index.com", "indexexchange.com")
	dom = dom.replace("improveddigital.com", "improvedigital.com").replace("improvedigitalimprovedigital.com", "improvedigital.com").replace("freewheel freewheel.tv", "freewheel.tv").replace("freewheel    freewheel.tv", "freewheel.tv")
	dom = dom.replace("ebemamae.comgoogle.com", "google.com").replace("d4c29acad76ce94f outbrain.com", "outbrain.com").replace("ctwant.com pubmatic.com", "pubmatic.com").replace("context web.com", "contextweb.com")
	
	if "." not in dom:
		dom = dom.replace("adsparc", "adsparc.com").replace("adsolut", "adsolut.in").replace("adswizz", "adswizz.com").replace("aol", "aol.com").replace("youtube", "youtube.com").replace("yahoo", "yahoo.com")
		dom = dom.replace("xandr", "xandr.com").replace("waardex", "waardex.com").replace("ucfunnel", "ucfunnel.com").replace("spotxchange", "spotxchange.com").replace("targetspot", "targetspot.com")
		dom = dom.replace("spotx.tvspotxchange.com", "spotx.tv").replace("sovrn", "sovrn.com").replace("smilewanted", "smilewanted.com").replace("rubicon", "rubiconproject.com")
		dom = dom.replace("revcontent", "revcontent.com").replace("quantum-advertising", "quantum-advertising.com").replace("q1connect", "q1connect.com").replace("pubmatic", "pubmatic.com")
		dom = dom.replace("google", "google.com").replace("taboola", "taboola.com").replace("spotx", "spotx.tv")
	
	replace_patterns = ["​", "*.go.", "ï»¿ï»¿", "ï»¿", "...", "34	", "39	", "40	", "41	", "42	", "5d62403b186f2ace ", "?", "\\u{200b}", "acd.op.", "appnexus    ", 
						"api.publishers.", " (http://appnexus.com/)", "<http://appnexus.com/>", "beachfront ", "ãƒæ’ã†â€™ãƒâ€ ã¢â‚¬â„¢ãƒæ’ã¢â‚¬ ãƒâ¢ã¢â€šâ¬ã¢â€žâ¢ãƒæ’ã†â€™ãƒâ¢ã¢â€šâ¬ã…â¡ãƒæ’ã¢â‚¬å¡ãƒâ€šã‚â¯ãƒæ’ã†â€™ãƒâ€ ã¢â‚¬â„¢ãƒæ’ã‚â¢ãƒâ¢ã¢â‚¬å¡ã‚â¬ãƒâ€¦ã‚â¡ãƒæ’ã†â€™ãƒâ¢ã¢â€šâ¬ã…â¡ãƒæ’ã¢â‚¬å¡ãƒâ€šã‚â»ãƒæ’ã†â€™ãƒâ€ ã¢â‚¬â„¢ãƒæ’ã‚â¢ãƒâ¢ã¢â‚¬å¡ã‚â¬ãƒâ€¦ã‚â¡ãƒæ’ã†â€™ãƒâ¢ã¢â€šâ¬ã…â¡ãƒæ’ã¢â‚¬å¡ãƒâ€šã‚â¿",
						"ã¯â»â¿", "ã¢â‚¬â€¹", "â€‹", "â", " (http://yahoo.com/)", " (http://video.unrulymedia.com/)", "verizon media group: ", "verizon marketplace: ",
						"verizon ", "usa today    ", " [linkprotect.cudasvc.com]", "triplelift ", "tremor - ", "ã", " [link.edgepilot.com] [link.edgepilot.com] [link.edgepilot.com] [link.edgepilot.com]",
						" (http://synacor.com/)", " [spotxchange.com]", " [spotx.tv]", " (http://sonobi.com/)", " (http://smaato.com/)", " (http://rubiconproject.com/)", " (http://revcontent.com/)",
						" [openx.com]", "oath - ", "o;?", "newtalk.tw  ", "lkqd    ", "<http://google.com>", " (http://google.com/)", "google adx    ", "fyber - ", 
						" (http://improvedigital.com/)", "improve    ", "https://www.", "https://", "http://", "/", "www.", "(transfermarkt)", "<http://freewheel.tv>",
						" (http://emxdgt.com/)", "day:", "<http://contextweb.com>", "cignal        ", "cignal.io        ", "connatix    ", "web: ", "website: www.", "xumo: ", 
						"xumo lg: ", "unrulyx: ", "sovrn: ", "smaato: ", "pulsepoint: ", "pubmatic: ", "pubmatic apac: ", "pubmatic eu: ", "openx: ", "instream: ", "index exchange: ", 
						"emx digital: ", "dmx: ", "acuity: ", "amazon: ", "brainly s2s amazon: ", "brainly: ", "smartrtb: ", "loopme    "]
	for pattern in replace_patterns:
		dom = dom.replace(pattern, "")


	if dom == "adcolony.com 496220845654deec reseller 1ad675c9de6b5176":
		return "adcolony.com", True, "496220845654deec"
	if dom == "adview.com 58850823 direct":
		return "adview.com", True, "58850823"
	if dom == "criteo.com; 9332; direct":
		return "criteo.com", True, "9332"
	if dom == "inmobi.com 94d702ada29c4b059e9aca837748b9fc reseller 83e75a7ae333ca9d":
		return "inmobi.com", True, "94d702ada29c4b059e9aca837748b9fc"
	if dom == "jeeng.com||1937":
		return "jeeng.com", True, "1937"
	if dom == "mars.media 102825":
		return "mars.media", True, "102825"
	if dom == "mobilefuse.com 2281 reseller 71e88b065d69c021":
		return "mobilefuse.com", True, "2281"
	if dom == "richaudience.com ua8biwjxkr reseller":
		return "richaudience.co", True, "ua8biwjxkr"
	if dom == "run-syndicate.com 809":
		return "run-syndicate.com", True, "809"
	if dom == "runative-syndicate.com 809":
		return "runative-syndicate.com", True, "809"
	if dom == "sharethrough.com 0d60edd5 reseller":
		return "sharethrough.com", True, "0d60edd5"
	if dom == "smartyads.com 23":
		return "smartyads.com", True, "23"
	if dom == "yldbt.com 5b522cc167f6b300b89dc6d3 reseller cd184cb30abaabb5":
		return "yldbt.com", True, "5b522cc167f6b300b89dc6d3"
	if dom == "appnexus":
		return "appnexus.com", True, "NA"

	if dom in ["adcolony", "adops", "adtag.vidmatic.com", "adtag.vidssp.com", "adyoulke.com", "apnexus.com", "app: aps.amazon.com", "appnexuscom", "bizzclick", "bizzclick.net", "brainly s2s yahoo.com", "ccontextweb.com", "ccoxmt.com", "chinatimes.com indexexchange.com", "cpmstar", "cpubmatic.com", "criteo.net", "dailymotion", "districtm", "districtm: appnexus.com", "eappnexus.com", "emxdgt.com", "emxdigital.com", "emxgdt.com", "emxgt.com", "engageadx", "eplanning.net", "epom", "epom.com", "exponential.com", "exponential.comi", 
				"fmlabsonline", "freestar.io", "freewheel.tv", "freewheel", "go.sonobi.com", "i33across.com", "ijit.com", "index", "indexexchage.com", "indexexchange", "infolinks", "inventorypartnerdomain=failarmy.tv", "inventorypartnerdomain=firstimpression.io", "inventorypartnerdomain=peopleareawesome.tv", "inventorypartnerdomain=thepetcollective.tv", "inventorypartnerdomain=vuit.com", "inventorypartnerdomain=weatherspy.tv", "inventorypartnerdomain=wurl.com", "istrictm.io", 
				"kiwihk", "kqd.com", "kqd.net", "ligit.com", "lijit.copenx.com", "limpid", "magnite", "magnite: rubiconproject.com", "mahimeta", "mapmyfitness liveintent.com", "media-net", "mediaonline.com", "mobfox", "mobupps", "mobuppsrtb.com", "ndexexchange.com", "nsightvideo.com", "o;google.com", "openx", "openx.comm", "openx.net", "outbrain.cbuffom",  
				"penx.com", "pera.media", "potx.tv", "potxchange.com", "ppnexus.com", "publisher.phunware.com", "publishers.adlive.io", "publishers.logicad.jp", "publishers.teads.tv", "pubnative.com", "quantumdx.io", "relaido", "relaido.jp", "rhythmone", "rhythmone.cpm", "rhythomone.com", "riteo.com", "rtbhhouse.com", "rtbhouse", "sekindo", "sharethrough: sharethrough.com", "smartadserver", "sonictwist", 
				"spot.im", "spotexchange.com", "spotim.market", "spotx.com","spotx.tvchange.com", "spotx.tvspotxchange.com", "spotxchange.com", "sulvo.co", "sulvo.com", "syancor.com", "teads.tv", "test.e-planning.net", "themediagrid.com", "themoneytizer.com‚", "tpmn.co.kr", "triplift.com", 
				"viads.co", "video advertising.com", "website: interplaymedia.com.au", "yieldlab.de", "yieldlab.net", "yieldmo", "﻿anyclip.com", "﻿appnexus.com", "﻿google.com", "﻿improvedigital.com", "﻿spotxchange.com", "﻿﻿appnexus.com", "﻿﻿inmobi.com", "﻿﻿rubiconproject.com", "﻿﻿video.unrulymedia.com"]:
		dom = dom.replace("adcolony", "adcolony.com").replace("adops", "adops.com").replace("adtag.", "").replace("adyoulke.com", "adyoulike.com").replace("apnexus.com", "appnexus.com").replace("app: ", "").replace("appnexuscom", "appnexus.com").replace("bizzclick", "bizzclick.com").replace("bizzclick.net", "bizzclick.com").replace("brainly s2s ", "").replace("ccontextweb.com", "contextweb.com").replace("ccoxmt.com", "coxmt.com").replace("chinatimes.com ", "").replace("cpmstar", "cpmstar.com").replace("cpubmatic.com", "pubmatic.com").replace("criteo.net", "criteo.com").replace("dailymotion", "dailymotion.com").replace("districtm", "districtm.io").replace("districtm: ", "").replace("eappnexus.com", "appnexus.com").replace("emxdgt.com", "emxdigital.com").replace("emxgdt.com", "emxdigital.com").replace("emxgt.com", "emxdigital.com").replace("engageadx", "engageadx.com").replace("epom", "epom.com").replace("exponential.comi", "exponential.com").replace("eplanning.net", "e-planning.net")
		dom = dom.replace("fmlabsonline", "fmlabsonline.com").replace("freestar.io", "freestar.com").replace("freewheel.tv", "freewheel.com").replace("freewheel", "freewheel.com").replace("go.sonobi.com", "sonobi.com").replace("i33across.com", "33across.com").replace("ijit.com", "lijit.com").replace("index", "indexexchange.com").replace("indexexchage.com", "indexexchange.com").replace("indexexchange", "indexexchange.com").replace("infolinks", "infolinks.com").replace("inventorypartnerdomain=", "").replace("istrictm.io", "districtm.io")
		dom = dom.replace("kiwihk", "kiwihk.net").replace("kqd.com", "lkqd.com").replace("kqd.net", "lkqd.net").replace("ligit.com", "lijit.com").replace("lijit.copenx.com", "openx.com").replace("limpid", "limpid.tv").replace("magnite: ", "").replace("mahimeta", "mahimeta.com").replace("mapmyfitness ", "").replace("media-net", "media.net").replace("mediaonline.com", "9mediaonline.com").replace("mobfox", "mobfox.com").replace("mobupps", "mobupps.com").replace("mobuppsrtb.com", "mobupps.com").replace("ndexexchange.com", "indexexchange.com").replace("o;google.com", "google.com").replace("openx", "openx.com").replace("openx.comm", "openx.com").replace("openx.net", "openx.com").replace("outbrain.cbuffo", "outbrain.com")
		dom = dom.replace("penx.com", "openx.com").replace("pera.media", "opera.com").replace("potx.tv", "spotx.tv").replace("potxchange.com", "spotx.tv").replace("ppnexus.com", "appnexus.com").replace("publisher.", "").replace("publishers.", "").replace("pubnative.com", "pubnative.net").replace("quantumdx.io", "quantumdex.io").replace("relaido", "relaido.jp").replace("rhythmone", "rhythmone.com").replace("rhythmone.cpm", "rhythmone.com").replace("rhythomone.com", "rhythmone.com").replace("riteo.com", "criteo.com").replace("rtbhouse", "rtbhouse.com").replace("rtbhhouse.com", "rtbhouse.com").replace("sekindo", "sekindo.com").replace("sharethrough: ", "").replace("smartadserver", "smartadserver.com").replace("sonictwist", "sonictwist.media")
		dom = dom.replace("spotexchange.com", "spotx.tv").replace("spotx.com", "spotx.tv").replace("spotx.tvchange.com", "spotx.tv").replace("spotx.tvspotxchange.com", "spotx.tv").replace("spotxchange.com", "spotx.tv").replace("sulvo.co", "sulvo.com").replace("syancor.com", "synacor.com").replace("teads.tv", "teads.com").replace("spot.im", "spotim.market").replace("test.e-planning.net", "e-planning.net").replace("themoneytizer.com‚", "themoneytizer.com").replace("tpmn.co.kr", "tpmn.io").replace("triplift.com", "triplelift.com")
		dom = dom.replace("viads.co", "viads.com").replace("video ", "").replace("weborama.nl", "").replace("website: ", "").replace("yieldlab.de", "yieldlab.com").replace("yieldlab.net", "yieldlab.com").replace("yieldmo", "yieldmo.com").replace("﻿", "")


	return dom, True, "NA"



def get_pool_owner_domain(ad_domain, seller_id):
	filename = str(sellersjson_dir) + "/" + str(ad_domain).replace(".","_") + ".json"
	try:
		f = open(filename)
	except BaseException as e:
		return "sellersjson_not_available"

	ad_sellers = {}
	seller_domain = ""
	if ad_domain in ["google.com"]:
		ad_sellers = json.loads(ast.literal_eval(json.dumps(f.read())))
	else:
		json_string = json.load(f)
		ad_sellers = json.loads(json_string)

	for seller in ad_sellers["sellers"]:
		item_list = []
		sid = "NA"
		is_confidential = "False"
		seller_domain = "unused_seller_id"

		if "seller_id" in seller.keys():
			sid = str(seller["seller_id"]).strip().lower()
			if sid == seller_id:				
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
	
	seller_domain = seller_domain.replace("​", "").replace("/", "").replace("aps.amazon.comapsindex.html", "aps.amazon.com").replace("disqus", "disqus.com").replace("mediavine.comsellers.json", "mediavine.com").replace("aps.amazon.comapsunified-ad-marketplace", "aps.amazon.com")
	return seller_domain
			



def parse_adstxt(ad_sellers):
	all_sellers = []
	for seller in ad_sellers:
		item_list = []
			
		s = seller
		if "#" in seller:
			s = seller[:seller.index("#")]

		if len(s) < 5:
			continue
		else:
			temp = s.split(",")
			# print(temp)
			item_list.append(temp[0].strip().lower())
			if len(temp) >= 2:
				if temp[1].strip() == "":
					item_list.append("NA")
				else:
					item_list.append(temp[1].strip().lower())

				if len(temp) >= 3:
					if temp[2].strip() == "":
						item_list.append("NA")
					else:
						item_list.append(temp[2].strip().upper())

					if len(temp) >= 4:
						if temp[3].strip() == "":
							item_list.append("NA")
						else:
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
	l = dfs[(dfs["ad_domain"] == adom)]["seller_id"].unique().tolist()
	if sid in l:
		return True
	else:
		return False




for i in range(len(df)):
	# print(i)
	misinfo_domain = str(df.iloc[i]["misinformation_domain"]).strip().lower().replace("https://","").replace("http://","").replace("www.","")
	adstxt_presence = str(df.iloc[i]["adstxt_presence"])
	seller_type = str(df.iloc[i]["seller_account_type"])
	print(misinfo_domain)
	# if "babylonbee" not in misinfo_domain:
	# 	continue
	
	
	ad_domain, flag, sid = process_ad_domain(str(df.iloc[i]["ad_domain"]))
	if flag == False:
		continue

	if sid != "NA":
		seller_id = sid
	else:
		seller_id, flag = process_seller_id(str(df.iloc[i]["seller_id"]))
		if flag == False:
			continue

	if misinfo_domain not in misinformation_domains:
		misinformation_domains.append(misinfo_domain)

	if adstxt_presence == "Yes":
		pool_str = ad_domain + "|" + seller_id
		domain_str = misinfo_domain + "|M"

		check_flag = False
		if seller_type == "RESELLER":
			# If the ad_domain is a mentioned as "RESELLER" in ads.txt and 
			# If its also a valid "INTERMEDIARY"/"BOTH" in corresponding sellers.json entry, then its not dark pooling
			check_flag = check_reseller_relationship(ad_domain, seller_id)

		if check_flag == True:
			continue

		if pool_str not in dark_pools.keys():
			dark_pools[pool_str] = {"Misinfo_Pool": []}
		dark_pools[pool_str]["Misinfo_Pool"].append(domain_str)


# print(dark_pools)
print("Summary Ads TXT analysed.")


for file in os.listdir(adstxt_dir):
	print(os.listdir(adstxt_dir).index(file), file)

	if ".DS_Store" in file:
		continue
	
	top_100k_domain = str(file.split("|")[1]).replace("_",".").replace(".txt","").strip().lower()
	domain_str = top_100k_domain + "|O"

	if top_100k_domain in misinformation_domains:
		continue
	
	f = open(adstxt_dir + "/" + str(file), "r")
	adstxt_lines = f.read().split("\n")
	adstxt_sellers = parse_adstxt(adstxt_lines)

	for seller in adstxt_sellers:
		ad_domain, flag, sid = process_ad_domain(str(seller[0]))
		if flag == False:
			continue

		if sid != "NA":
			seller_id = sid
		else:
			seller_id, flag = process_seller_id(str(seller[1]))
			if flag == False:
				continue

		pool_str = ad_domain + "|" + seller_id
		# print(pool_str)

		seller_type = str(seller[0]).upper()
		check_flag = False
		if seller_type == "RESELLER":
			check_flag = check_reseller_relationship(ad_domain, seller_id)

		if check_flag == True:
			continue

		if pool_str in dark_pools.keys():
			if "Misinfo_Pool" in dark_pools[pool_str].keys():
				dark_pools[pool_str]["Misinfo_Pool"].append(domain_str)
			elif "Other_Pool" in dark_pools[pool_str].keys():
				dark_pools[pool_str]["Other_Pool"].append(domain_str)
		elif pool_str not in dark_pools.keys():
			dark_pools[pool_str] = {"Other_Pool": []}
			dark_pools[pool_str]["Other_Pool"].append(domain_str)


fo = open("control_dark_pools.txt", "w")
fo.write("pool_type, ad_domain|seller_id, pool_owner_domain, pool_size, domains_sharing_pool")
fo.write("\n")


for pool in dark_pools.keys():
	if "Misinfo_Pool" in dark_pools[pool].keys():
		pool_size = len(list(set(dark_pools[pool]["Misinfo_Pool"])))
		if pool_size > 1:
			ad_dom = pool.split("|")[0].lower()
			sid = pool.split("|")[1].lower()
			sdom = get_pool_owner_domain(ad_dom, sid)

			print("Misinfo_Pool, " + str(pool) + ", " + str(sdom) + ", " + str(pool_size) + ", " + "; ".join(list(set(dark_pools[pool]["Misinfo_Pool"]))))
			outp_str = "Misinfo_Pool, " + str(pool) + ", " + str(sdom) + ", " + str(pool_size) + ", " + "; ".join(list(set(dark_pools[pool]["Misinfo_Pool"])))
			fo.write(outp_str)
			fo.write("\n")

'''
for pool in dark_pools.keys():
	if "Other_Pool" in dark_pools[pool].keys():
		pool_size = len(list(set(dark_pools[pool]["Other_Pool"])))
		if pool_size > 1:
			ad_dom = pool.split("|")[0].lower()
			sid = pool.split("|")[1].lower()
			sdom = get_pool_owner_domain(ad_dom, sid)

			print("NonMisinfo_Pool, " + str(pool) + ", " + str(sdom) + ", " + str(pool_size) + ", " + "; ".join(list(set(dark_pools[pool]["Other_Pool"]))))
			outp_str = "NonMisinfo_Pool, " + str(pool) + ", " + str(sdom) + ", " + str(pool_size) + ", " + "; ".join(list(set(dark_pools[pool]["Other_Pool"])))
			fo.write(outp_str)
			fo.write("\n")
'''

fo.close()
