import os
import datetime
import requests
import urllib3
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from dotenv import load_dotenv
from serpapi import GoogleSearch
from supabase import create_client, Client

# Dölj Streamlit-meny, GitHub-ikon och fotnot
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden; display: none !important;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    </style>
"""

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden; display: none !important;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stStatusWidget"] {visibility: hidden;}
    .viewerBadge_container__1QSob,
    .viewerBadge_link__1S137,
    [class*="viewerBadge"] {display: none !important;}
    footer:after {content: ""; display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
WHOLESALE_DOMAINS = ["aliexpress.com", "temu.com", "1688.com", "taobao.com", "dhgate.com"]

# --- UX & DESIGN CONFIG ---
st.set_page_config(
    page_title="DropShipKollen – Avslöja Kinakopiorna", 
    page_icon="🕵️‍♂️", 
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            text-align: center;
        }

        div[data-testid="stTabs"] {
            margin-bottom: 2rem;
            border-bottom: none !important;
        }

        div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: #F1F5F9;
            padding: 6px;
            border-radius: 12px;
            border: 1px solid #E2E8F0;
            width: fit-content;
            margin: 0 auto;
        }

        div[data-testid="stTabs"] [data-baseweb="tab"] {
            height: 42px;
            padding: 0 20px;
            background-color: transparent;
            border-radius: 8px;
            border: none !important;
            color: #64748B;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.2s ease;
        }

        div[data-testid="stTabs"] [data-baseweb="tab"]:hover {
            color: #0F172A;
        }

        div[data-testid="stTabs"] [aria-selected="true"] {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            font-weight: 700 !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
        }

        div[data-testid="stTabs"] [data-baseweb="tab-border"],
        div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
        div[data-testid="stTabs"] hr {
            display: none !important;
            border: none !important;
            height: 0px !important;
        }

        .hero-container {
            text-align: center;
            margin-bottom: 1.5rem;
        }

        .badge {
            display: inline-block;
            background: #FEE2E2;
            color: #DC2626;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.3px;
            margin-bottom: 14px;
            border: 1px solid #FECACA;
        }

        .hero-title {
            font-size: 2.8rem;
            font-weight: 800;
            line-height: 1.15;
            letter-spacing: -0.02em;
            color: #0F172A;
            margin-bottom: 12px;
            text-align: center;
        }

        .hero-subtitle {
            font-size: 1.1rem;
            color: #64748B;
            margin: 0 auto 24px auto;
            max-width: 620px;
            line-height: 1.5;
            text-align: center;
        }

        div[data-testid="stTextInput"] label {
            width: 100%;
            text-align: center;
            font-weight: 600;
            font-size: 1rem;
            color: #1E293B;
        }

        div[data-testid="stTextInput"] input {
            text-align: center;
        }

        .step-box {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px 14px;
            text-align: center;
            height: 100%;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        }
        .step-icon {
            font-size: 1.8rem;
            margin-bottom: 8px;
        }
        .step-title {
            font-weight: 700;
            font-size: 0.95rem;
            color: #0F172A;
            margin-bottom: 4px;
        }
        .step-desc {
            font-size: 0.82rem;
            color: #64748B;
            line-height: 1.35;
        }

        div[data-testid="stMetric"] {
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        div[data-testid="stMetricLabel"] {
            justify-content: center;
        }

        .guide-text {
            text-align: center;
            line-height: 1.6;
            color: #334155;
            margin-bottom: 1.5rem;
        }

        .affiliate-note {
            font-size: 0.75rem;
            color: #94A3B8;
            margin-top: 6px;
            text-align: center;
        }

        [data-testid="collapsedControl"] {
            position: relative;
        }
        [data-testid="collapsedControl"]:hover::after {
            content: "Senaste sökningar på sidan";
            position: absolute;
            left: 48px;
            top: 50%;
            transform: translateY(-50%);
            white-space: nowrap;
            background: #0F172A;
            color: #FFFFFF;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
            pointer-events: none;
            z-index: 999999;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18);
        }

        [data-testid="stSidebarCollapseButton"] {
            position: relative;
        }
        [data-testid="stSidebarCollapseButton"]:hover::after {
            content: "Dölj senaste sökningar";
            position: absolute;
            right: 48px;
            top: 50%;
            transform: translateY(-50%);
            white-space: nowrap;
            background: #0F172A;
            color: #FFFFFF;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
            pointer-events: none;
            z-index: 999999;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18);
        }

        .stButton>button {
            border-radius: 10px;
            font-weight: 700;
            font-size: 1.05rem;
            padding: 12px 24px;
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(220, 38, 38, 0.2);
        }
    </style>
""", unsafe_allow_html=True)

def scrape_generic_page(url: str):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        
        title_tag = soup.find("meta", property="og:title")
        title = title_tag["content"] if title_tag and title_tag.get("content") else soup.title.string if soup.title else "Okänd produkt"
        
        img_tag = soup.find("meta", property="og:image")
        img_url = img_tag["content"] if img_tag and img_tag.get("content") else None
        
        if img_url and img_url.startswith("//"):
            img_url = "https:" + img_url
            
        if not img_url:
            return None
            
        return {
            "title": title.strip(),
            "price": "Se länk",
            "image_url": img_url
        }
    except Exception:
        return None

def get_product(store_url: str):
    store_url = store_url.strip()
    if not store_url.startswith("http"):
        store_url = "https://" + store_url
        
    parsed = urlparse(store_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    if "/products/" in parsed.path:
        endpoint = f"{base_url}{parsed.path}.json"
        is_single_product = True
    else:
        endpoint = f"{base_url}/products.json?limit=1"
        is_single_product = False
        
    try:
        res = requests.get(endpoint, headers=HEADERS, timeout=8, verify=False)
        if res.status_code == 200:
            data = res.json()
            if is_single_product:
                prod = data.get("product")
                if prod:
                    img_url = prod.get("images", [{}])[0].get("src") if prod.get("images") else None
                    if img_url and img_url.startswith("//"): img_url = "https:" + img_url
                    return {
                        "title": prod.get("title", "Okänd"),
                        "price": prod.get("variants", [{}])[0].get("price", "N/A"),
                        "image_url": img_url
                    }
            else:
                products = data.get("products", [])
                if products:
                    prod = products[0]
                    img_url = prod.get("images", [{}])[0].get("src") if prod.get("images") else None
                    if img_url and img_url.startswith("//"): img_url = "https:" + img_url
                    return {
                        "title": prod.get("title", "Okänd"),
                        "price": prod.get("variants", [{}])[0].get("price", "N/A"),
                        "image_url": img_url
                    }
    except Exception:
        pass
        
    return scrape_generic_page(store_url)

def find_match(image_url: str):
    params = {"engine": "google_lens", "url": image_url, "api_key": SERPAPI_KEY, "country": "se", "hl": "sv"}
    try:
        search = GoogleSearch(params)
        for match in search.get_dict().get("visual_matches", []):
            link = match.get("link", "").lower()
            for domain in WHOLESALE_DOMAINS:
                if domain in link:
                    price_info = match.get("price", {})
                    price = price_info.get("extracted_value") or price_info.get("value", "N/A")
                    currency = price_info.get("currency", "")
                    return {
                        "source": domain.split(".")[0].capitalize(),
                        "url": match.get("link"),
                        "price": f"{price} {currency}".strip(),
                        "title": match.get("title")
                    }
    except Exception:
        pass
    return None

def check_domain_history(store_url: str):
    try:
        parsed = urlparse(store_url if store_url.startswith("http") else "https://" + store_url)
        domain = parsed.netloc.replace("www.", "")
        
        response = supabase.table("scraped_products").select("*").ilike("store_url", f"%{domain}%").execute()
        
        if response.data:
            red_flags = [item for item in response.data if item.get("dropship_source")]
            return len(red_flags) > 0, domain
    except Exception:
        pass
    return False, ""

def get_existing_search(store_url: str):
    try:
        normalized_url = store_url.strip()
        response = supabase.table("scraped_products").select("*").eq("store_url", normalized_url).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
    except Exception:
        pass
    return None

# --- HANTERA URL VIA QUERY PARAMS ---
query_params = st.query_params
selected_url_from_history = query_params.get("url", None)

# --- SIDOBAR FÖR HISTORIK ---
with st.sidebar:
    st.markdown("<h3 style='text-align: center;'>🕒 Senast granskade</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size: 0.85rem;'>Klicka på en produkt för att ladda granskningen direkt.</p>", unsafe_allow_html=True)
    
    filter_choice = st.selectbox(
        "Filtrera:",
        ["Alla", "🚨 Endast Dropshipping", "✅ Endast Rena"]
    )
    
    st.divider()
    
    try:
        response = supabase.table("scraped_products").select("*").order("scraped_at", desc=True).limit(20).execute()
        recent_items = response.data
        
        if not recent_items:
            st.info("Inga sökningar gjorda än.")
        else:
            filtered_items = []
            for item in recent_items:
                is_dropship = bool(item.get("dropship_source"))
                if filter_choice == "Alla":
                    filtered_items.append(item)
                elif filter_choice == "🚨 Endast Dropshipping" and is_dropship:
                    filtered_items.append(item)
                elif filter_choice == "✅ Endast Rena" and not is_dropship:
                    filtered_items.append(item)
            
            filtered_items = filtered_items[:6]
            
            if not filtered_items:
                st.info("Inga träffar för detta filter.")
            else:
                for item in filtered_items:
                    title = item.get('store_title', 'Okänd produkt')
                    item_url = item.get('store_url', '')
                    is_dropship = bool(item.get("dropship_source"))
                    badge_label = f"🚨 {item.get('dropship_source')}" if is_dropship else "✅ Grön flagg"
                    
                    with st.container(border=True):
                        st.markdown(f"<div style='text-align: center; font-weight: 700;'>{title[:32]}...</div>" if len(title) > 32 else f"<div style='text-align: center; font-weight: 700;'>{title}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align: center; color: #64748B; font-size: 0.8rem; margin-bottom: 8px;'>{badge_label}</div>", unsafe_allow_html=True)
                        if st.button("Visa granskning", key=f"hist_{item['id']}", use_container_width=True):
                            st.query_params["url"] = item_url
                            st.rerun()
    except Exception:
        st.error("Kunde inte ladda historik.")

# --- TOPPMENY ---
tab_search, tab_about = st.tabs(["🔍 Granska Butik", "📖 Konsumentguide"])

with tab_search:
    # Hero
    st.markdown("""
        <div class="hero-container">
            <div class="badge">🛡️ KONSUMENTKONTROLL</div>
            <div class="hero-title">Bli inte lurad av överpriser.</div>
            <div class="hero-subtitle">Många nätbutiker säljer billiga artiklar från Kina med 500% påslag. Klistra in en länk så söker vi efter originalkällan på 5 sekunder.</div>
        </div>
    """, unsafe_allow_html=True)

    default_url = selected_url_from_history if selected_url_from_history else ""
    store_url = st.text_input(
        "Klistra in länk till butik eller produkt:",
        value=default_url,
        placeholder="https://butik.se/products/snygg-klocka"
    )

    if selected_url_from_history:
        st.query_params.clear()

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        run_search = st.button("Avslöja produkten 🔍", type="primary", use_container_width=True)

    if not run_search and not selected_url_from_history:
        st.write("")
        st.write("")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
                <div class="step-box">
                    <div class="step-icon">🔗</div>
                    <div class="step-title">1. Klistra in</div>
                    <div class="step-desc">Kopiera webbadressen från butiken du vill granska.</div>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
                <div class="step-box">
                    <div class="step-icon">🤖</div>
                    <div class="step-title">2. AI-matchning</div>
                    <div class="step-desc">Vi bildsöker direkt mot Temu, AliExpress & grossister.</div>
                </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown("""
                <div class="step-box">
                    <div class="step-icon">💡</div>
                    <div class="step-title">3. Se sanningen</div>
                    <div class="step-desc">Få originalkällan, prisjämförelse och varningar direkt.</div>
                </div>
            """, unsafe_allow_html=True)

    if run_search or selected_url_from_history:
        target_url = store_url.strip()
        if not target_url:
            st.warning("⚠️ Vänligen klistra in en fungerande webbadress först.")
        else:
            existing_result = get_existing_search(target_url)
            
            if existing_result:
                st.info("⚡ **Resultat hämtat från arkivet!** Produkten har redan granskats nyligen.")
                
                item_title = existing_result.get("store_title", "Okänd")
                item_price = existing_result.get("store_price", "N/A")
                dropship_source = existing_result.get("dropship_source")
                dropship_url = existing_result.get("dropship_url")
                
                product = get_product(target_url)
                img_to_show = product["image_url"] if product else "https://via.placeholder.com/400"
                
                st.divider()
                
                if dropship_source:
                    st.error("🚨 **DROPSHIPPING BEKRÄFTAT!** Samma produkt finns hos en utländsk grossist.")
                    col1, col2 = st.columns(2)
                    with col1:
                        with st.container(border=True):
                            st.markdown("<h4 style='text-align: center;'>🛒 Butikens pris</h4>", unsafe_allow_html=True)
                            st.image(img_to_show, use_container_width=True)
                            st.metric(label="Pris i butik", value=f"{item_price} kr" if item_price != "N/A" else "Ej angivet")
                            st.caption(f"<div style='text-align: center;'>{item_title}</div>", unsafe_allow_html=True)
                    with col2:
                        with st.container(border=True):
                            st.markdown("<h4 style='text-align: center;'>📦 Grossistens original</h4>", unsafe_allow_html=True)
                            st.success(f"Hittad hos **{dropship_source}**")
                            st.metric(label="Uppskattat grossistpris", value="Se länk")
                            st.caption(f"<div style='text-align: center;'>{item_title}</div>", unsafe_allow_html=True)
                            if dropship_url:
                                st.link_button(f"Gå till originalet på {dropship_source} ↗", dropship_url, type="secondary", use_container_width=True)
                                st.markdown('<div class="affiliate-note">* Länken är en potentiell annonslänk som stödjer driften av tjänsten.</div>', unsafe_allow_html=True)
                else:
                    st.success("✅ **GRÖN FLAGG!** Inga tecken på dropshipping hittades för denna länk.")
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        st.image(img_to_show, caption=item_title, use_container_width=True)
                        
            else:
                has_previous_red_flags, domain_name = check_domain_history(target_url)
                product = None
                match = None
                
                with st.status("🔍 Granskar produkten och nätbutiken...", expanded=True) as status:
                    st.write("Hämtar bild och specifikationer...")
                    product = get_product(target_url)
                    
                    if not product or not product["image_url"]:
                        status.update(label="Kunde inte läsa in sidan", state="error", expanded=False)
                        st.error("Kunde inte hitta någon produktbild på sidan. Dubbelkolla länken.")
                    else:
                        st.write(f"Identifierade: **{product['title']}**")
                        st.write("Skannar databaser och bildmatchar med Google Lens...")
                        match = find_match(product["image_url"])
                        status.update(label="Analysen är klar!", state="complete", expanded=False)

                if product and product["image_url"]:
                    st.divider()
                    
                    dropship_source = match['source'] if match else None
                    dropship_url = match['url'] if match else None

                    db_data = {
                        "store_url": target_url,
                        "store_title": product['title'],
                        "store_price": str(product['price']),
                        "dropship_source": dropship_source,
                        "dropship_url": dropship_url,
                        "scraped_at": datetime.datetime.now().isoformat()
                    }
                    
                    try:
                        supabase.table("scraped_products").insert(db_data).execute()
                    except Exception:
                        pass

                    if match:
                        st.error("🚨 **DROPSHIPPING BEKRÄFTAT!** Samma produkt finns hos en asiatisk grossist till en bråkdel av priset.")
                        col1, col2 = st.columns(2)
                        with col1:
                            with st.container(border=True):
                                st.markdown("<h4 style='text-align: center;'>🛒 Butikens erbjudande</h4>", unsafe_allow_html=True)
                                st.image(product["image_url"], use_container_width=True)
                                st.metric(label="Pris i butiken", value=f"{product['price']} kr" if product['price'] != "N/A" else "Ej angivet")
                                st.caption(f"<div style='text-align: center;'>{product['title']}</div>", unsafe_allow_html=True)
                        with col2:
                            with st.container(border=True):
                                st.markdown("<h4 style='text-align: center;'>📦 Grossistens original</h4>", unsafe_allow_html=True)
                                st.info(f"📍 Originalkälla: **{match['source']}**")
                                st.metric(label="Grossistpris", value=match['price'] if match['price'] != "N/A" else "Se länk")
                                st.caption(f"<div style='text-align: center;'>{match['title']}</div>", unsafe_allow_html=True)
                                st.link_button(f"Gå till originalet på {match['source']} ↗", match['url'], type="secondary", use_container_width=True)
                                st.markdown('<div class="affiliate-note">* Länken är en potentiell annonslänk som stödjer driften av tjänsten.</div>', unsafe_allow_html=True)
                    
                    elif has_previous_red_flags:
                        st.warning(f"⚠️ **VARNING: BLANDAT UTBUD**\n\nJust denna produkt ser ren ut, men **{domain_name}** har tidigare fällts för dropshipping i vårt system. Många butiker blandar unika varor med billig kinareport för att vilseleda kunden. Var vaksam!")
                        col1, col2, col3 = st.columns([1,2,1])
                        with col2:
                            st.image(product["image_url"], caption=product['title'], use_container_width=True)

                    else:
                        st.success("✅ **GRÖN FLAGG!** Inga matchningar mot kända grossister hittades för denna artikel, och butiken har ett rent register.")
                        col1, col2, col3 = st.columns([1,2,1])
                        with col2:
                            st.image(product["image_url"], caption=product['title'], use_container_width=True)

with tab_about:
    st.markdown("<h3 style='text-align: center;'>Vad är egentligen Drop-shipping?</h3>", unsafe_allow_html=True)
    st.markdown("""
        <div class="guide-text">
        Dropshipping i sig är inte en olaglig eller dålig affärsmodell – det är helt enkelt en logistisk lösning där en e-handlare säljer varor utan att ha ett eget lager, och låter en grossist skicka produkten direkt till kunden.<br><br>
        Problem uppstår dock när mellanhänder säljer massproducerade kinaprylar med <strong>300% till 800% påslag</strong> och marknadsför dem som unika, svenskgjorda eller exklusiva kvalitetsprodukter. Då betalar du ett enormt överpris för något du faktiskt kan köpa direkt själv.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>Hur fungerar det med skatter, moms och tull vid egenimport?</h3>", unsafe_allow_html=True)
    st.markdown("""
        <div class="guide-text">
        Om du väljer att handla direkt från lågprisjättar som Temu eller AliExpress (utan svensk mellanhand) är det viktigt att ha koll på reglerna för import utanför EU:<br><br>
        <strong>Moms:</strong> Svensk moms (25%) tas ut på alla varor som importeras till EU. På de stora marknadsplatserna betalar du oftast momsen direkt i kassan (via IOSS-systemet), vilket gör att paketet tullklareras automatiskt utan strul.<br><br>
        <strong>Tull och avgifter:</strong> EU har slopat den gamla tullfrihetsgränsen på 150 euro för småförsändelser. För varor som köps in via e-handel från länder utanför EU tillkommer en schablontull på 3 euro per artikel (för varor under 150 euro). För dyrare varor (över 150 euro) gäller ordinarie tullsats beroende på produkttyp.<br><br>
        <strong>Förtullningsavgift:</strong> Om e-handelsplatsen inte sköter momsinbetalningen i förväg, tar fraktbolaget (som PostNord) ut en administrativ avgift för tullhanteringen (ofta mellan 75 och 125 kr) när paketet når Sverige.<br><br>
        <strong>Slutsatsen?</strong> Genom att avslöja dropshipparna hjälper DropShipKollen dig att antingen handla varan till det pris den faktiskt är värd direkt från källan, eller att medvetet välja svenska e-handlare som erbjuder snabba leveranser, svensk konsumentköplag och riktig kundservice.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>Hur finansieras tjänsten? (Öppenhet & Affiliate)</h3>", unsafe_allow_html=True)
    st.markdown("""
        <div class="guide-text">
        DropShipKollen är och kommer alltid att vara <strong>helt gratis</strong> för konsumenter att använda.<br><br>
        För att täcka serverkostnader, API-anrop och vidareutveckling använder vi ibland affiliatelänkar (annonslänkar). När du klickar på en länk till ett original hos en grossist och handlar kan vi få en liten provision från plattformen – helt utan någon extra kostnad för dig.<br><br>
        Detta påverkar aldrig våra analysresultat eller bedömningar. Vårt mål är alltid att ge dig 100% oberoende och ärlig konsumentupplysning.
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center;'>Hur fungerar DropShipKollen?</h3>", unsafe_allow_html=True)
    st.markdown("""
        <div class="guide-text">
        Tjänsten hjälper dig att se igenom fasaden på några sekunder:<br>
        <strong>1. Skanning:</strong> Vi läser av produktinformation och bilder från webbutiken du vill kontrollera.<br>
        <strong>2. Visuell sökning:</strong> Med hjälp av avancerad bildmatchning (Google Lens-teknik) söker vi igenom de största asiatiska grossistplattformarna.<br>
        <strong>3. Avslöjande:</strong> Om samma produkt säljs till en bråkdel av priset hos en grossist, får du en varningsflagg direkt tillsammans med en direktlänk till originalet!
        </div>
    """, unsafe_allow_html=True)