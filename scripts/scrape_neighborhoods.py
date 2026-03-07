import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

"""
Scrape specific Lisbon neighborhoods: Ajuda and Alcantara
"""

from src.idealista_scraper import IdealistaScraper
import time
import os

print("=" * 60)
print("IDEALISTA NEIGHBORHOOD SCRAPER")
print("Target: Lisboa Area - 14 Neighborhoods")
print("=" * 60)

# Auto-detect headless mode in CI environments
is_ci = bool(os.getenv('CI') or os.getenv('GITHUB_ACTIONS'))
headless_mode = is_ci or os.getenv('HEADLESS', '').lower() == 'true'

if headless_mode:
    print("🤖 Running in HEADLESS mode (CI detected)")
else:
    print("🖥️  Running with VISIBLE browser")

scraper = IdealistaScraper(headless=headless_mode)

try:
    # Scrape Ajuda
    print("\n\n🏠 SCRAPING LISBOA, AJUDA...")
    ajuda_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='ajuda',
        typology=None,  # Get all typologies
        max_pages=5
    )

    if not ajuda_df.empty:
        print(f"\n📊 AJUDA RESULTS ({len(ajuda_df)} listings):")
        print(ajuda_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(ajuda_df, 'data/lisboa_ajuda_listings.csv')
    else:
        print("⚠️ No Ajuda listings found")

    # Wait between neighborhoods to avoid detection
    print("\nWaiting 10 seconds before next neighborhood...")
    time.sleep(10)

    # Scrape Alcantara
    print("\n\n🏠 SCRAPING LISBOA, ALCANTARA...")
    alcantara_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='alcantara',
        typology=None,  # Get all typologies
        max_pages=5
    )

    if not alcantara_df.empty:
        print(f"\n📊 ALCANTARA RESULTS ({len(alcantara_df)} listings):")
        print(alcantara_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(alcantara_df, 'data/lisboa_alcantara_listings.csv')
    else:
        print("⚠️ No Alcantara listings found")

    # Wait between neighborhoods to avoid detection
    print("\nWaiting 10 seconds before next neighborhood...")
    time.sleep(10)

    # Scrape Campolide
    print("\n\n🏠 SCRAPING LISBOA, CAMPOLIDE...")
    campolide_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='campolide',
        typology=None,  # Get all typologies
        max_pages=5
    )

    if not campolide_df.empty:
        print(f"\n📊 CAMPOLIDE RESULTS ({len(campolide_df)} listings):")
        print(campolide_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(campolide_df, 'data/lisboa_campolide_listings.csv')
    else:
        print("⚠️ No Campolide listings found")

    # Wait between neighborhoods to avoid detection
    print("\nWaiting 10 seconds before next neighborhood...")
    time.sleep(10)

    # Scrape Alfragide
    print("\n\n🏠 SCRAPING LISBOA, ALFRAGIDE...")
    alfragide_df = scraper.scrape_neighborhood(
        city='amadora',  # Alfragide is in Amadora municipality
        neighborhood='alfragide',
        typology=None,  # Get all typologies
        max_pages=5
    )

    if not alfragide_df.empty:
        print(f"\n📊 ALFRAGIDE RESULTS ({len(alfragide_df)} listings):")
        print(alfragide_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(alfragide_df, 'data/lisboa_alfragide_listings.csv')
    else:
        print("⚠️ No Alfragide listings found")

    # Wait between neighborhoods to avoid detection
    print("\nWaiting 10 seconds before next neighborhood...")
    time.sleep(10)

    # Scrape Amoreiras
    print("\n\n🏠 SCRAPING LISBOA, AMOREIRAS...")
    amoreiras_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='amoreiras',
        typology=None,
        max_pages=5
    )

    if not amoreiras_df.empty:
        print(f"\n📊 AMOREIRAS RESULTS ({len(amoreiras_df)} listings):")
        print(amoreiras_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(amoreiras_df, 'data/lisboa_amoreiras_listings.csv')
    else:
        print("⚠️ No Amoreiras listings found")

    # Wait between neighborhoods to avoid detection
    print("\nWaiting 10 seconds before next neighborhood...")
    time.sleep(10)

    # Scrape Campo de Ourique
    print("\n\n🏠 SCRAPING LISBOA, CAMPO DE OURIQUE...")
    campo_ourique_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='campo-de-ourique',
        typology=None,
        max_pages=5
    )

    if not campo_ourique_df.empty:
        print(f"\n📊 CAMPO DE OURIQUE RESULTS ({len(campo_ourique_df)} listings):")
        print(campo_ourique_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(campo_ourique_df, 'data/lisboa_campo_de_ourique_listings.csv')
    else:
        print("⚠️ No Campo de Ourique listings found")

    # Wait between neighborhoods to avoid detection
    print("\nWaiting 10 seconds before next neighborhood...")
    time.sleep(10)

    # Scrape Saldanha
    print("\n\n🏠 SCRAPING LISBOA, SALDANHA...")
    saldanha_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='saldanha',
        typology=None,
        max_pages=5
    )

    if not saldanha_df.empty:
        print(f"\n📊 SALDANHA RESULTS ({len(saldanha_df)} listings):")
        print(saldanha_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(saldanha_df, 'data/lisboa_saldanha_listings.csv')
    else:
        print("⚠️ No Saldanha listings found")

    # Wait between neighborhoods to avoid detection
    print("\nWaiting 10 seconds before next neighborhood...")
    time.sleep(10)

    # Scrape Picoas
    print("\n\n🏠 SCRAPING LISBOA, PICOAS...")
    picoas_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='picoas',
        typology=None,
        max_pages=5
    )

    if not picoas_df.empty:
        print(f"\n📊 PICOAS RESULTS ({len(picoas_df)} listings):")
        print(picoas_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(picoas_df, 'data/lisboa_picoas_listings.csv')
    else:
        print("⚠️ No Picoas listings found")

    # Wait between neighborhoods to avoid detection
    print("\nWaiting 10 seconds before next neighborhood...")
    time.sleep(10)

    # Scrape Estrela
    print("\n\n🏠 SCRAPING LISBOA, ESTRELA...")
    estrela_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='estrela',
        typology=None,
        max_pages=5
    )

    if not estrela_df.empty:
        print(f"\n📊 ESTRELA RESULTS ({len(estrela_df)} listings):")
        print(estrela_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(estrela_df, 'data/lisboa_estrela_listings.csv')
    else:
        print("⚠️ No Estrela listings found")

    # Wait between neighborhoods to avoid detection
    print("\nWaiting 10 seconds before next neighborhood...")
    time.sleep(10)

    # Scrape Restelo
    print("\n\n🏠 SCRAPING LISBOA, RESTELO...")
    restelo_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='restelo',
        typology=None,
        max_pages=5
    )

    if not restelo_df.empty:
        print(f"\n📊 RESTELO RESULTS ({len(restelo_df)} listings):")
        print(restelo_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(restelo_df, 'data/lisboa_restelo_listings.csv')
    else:
        print("⚠️ No Restelo listings found")

    # Wait between neighborhoods to avoid detection
    print("\nWaiting 10 seconds before next neighborhood...")
    time.sleep(10)

    # Scrape Belém
    print("\n\n🏠 SCRAPING LISBOA, BELÉM...")
    belem_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='belem',
        typology=None,
        max_pages=5
    )

    if not belem_df.empty:
        print(f"\n📊 BELÉM RESULTS ({len(belem_df)} listings):")
        print(belem_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(belem_df, 'data/lisboa_belem_listings.csv')
    else:
        print("⚠️ No Belém listings found")

    # Wait between neighborhoods to avoid detection
    print("\nWaiting 10 seconds before next neighborhood...")
    time.sleep(10)

    # Scrape Santos
    print("\n\n🏠 SCRAPING LISBOA, SANTOS...")
    santos_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='santos',
        typology=None,
        max_pages=5
    )

    if not santos_df.empty:
        print(f"\n📊 SANTOS RESULTS ({len(santos_df)} listings):")
        print(santos_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(santos_df, 'data/lisboa_santos_listings.csv')
    else:
        print("⚠️ No Santos listings found")

    # Wait between neighborhoods to avoid detection
    print("\nWaiting 10 seconds before next neighborhood...")
    time.sleep(10)

    # Scrape Benfica
    print("\n\n🏠 SCRAPING LISBOA, BENFICA...")
    benfica_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='benfica',
        typology=None,
        max_pages=5
    )

    if not benfica_df.empty:
        print(f"\n📊 BENFICA RESULTS ({len(benfica_df)} listings):")
        print(benfica_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(benfica_df, 'data/lisboa_benfica_listings.csv')
    else:
        print("⚠️ No Benfica listings found")

    # Wait between neighborhoods to avoid detection
    print("\nWaiting 10 seconds before next neighborhood...")
    time.sleep(10)

    # Scrape Carnide
    print("\n\n🏠 SCRAPING LISBOA, CARNIDE...")
    carnide_df = scraper.scrape_neighborhood(
        city='lisboa',
        neighborhood='carnide',
        typology=None,
        max_pages=5
    )

    if not carnide_df.empty:
        print(f"\n📊 CARNIDE RESULTS ({len(carnide_df)} listings):")
        print(carnide_df[['title', 'price', 'typology', 'location']].head(10))
        scraper.save_to_csv(carnide_df, 'data/lisboa_carnide_listings.csv')
    else:
        print("⚠️ No Carnide listings found")

    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE!")
    print("=" * 60)

    if not ajuda_df.empty:
        print(f"\n✓ Ajuda: {len(ajuda_df)} listings → data/lisboa_ajuda_listings.csv")
    if not alcantara_df.empty:
        print(f"✓ Alcantara: {len(alcantara_df)} listings → data/lisboa_alcantara_listings.csv")
    if not campolide_df.empty:
        print(f"✓ Campolide: {len(campolide_df)} listings → data/lisboa_campolide_listings.csv")
    if not alfragide_df.empty:
        print(f"✓ Alfragide: {len(alfragide_df)} listings → data/lisboa_alfragide_listings.csv")
    if not amoreiras_df.empty:
        print(f"✓ Amoreiras: {len(amoreiras_df)} listings → data/lisboa_amoreiras_listings.csv")
    if not campo_ourique_df.empty:
        print(f"✓ Campo de Ourique: {len(campo_ourique_df)} listings → data/lisboa_campo_de_ourique_listings.csv")
    if not saldanha_df.empty:
        print(f"✓ Saldanha: {len(saldanha_df)} listings → data/lisboa_saldanha_listings.csv")
    if not picoas_df.empty:
        print(f"✓ Picoas: {len(picoas_df)} listings → data/lisboa_picoas_listings.csv")
    if not estrela_df.empty:
        print(f"✓ Estrela: {len(estrela_df)} listings → data/lisboa_estrela_listings.csv")
    if not restelo_df.empty:
        print(f"✓ Restelo: {len(restelo_df)} listings → data/lisboa_restelo_listings.csv")
    if not belem_df.empty:
        print(f"✓ Belém: {len(belem_df)} listings → data/lisboa_belem_listings.csv")
    if not santos_df.empty:
        print(f"✓ Santos: {len(santos_df)} listings → data/lisboa_santos_listings.csv")
    if not benfica_df.empty:
        print(f"✓ Benfica: {len(benfica_df)} listings → data/lisboa_benfica_listings.csv")
    if not carnide_df.empty:
        print(f"✓ Carnide: {len(carnide_df)} listings → data/lisboa_carnide_listings.csv")

finally:
    scraper.driver.quit()
    print("\n✓ Browser closed")
