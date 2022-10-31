import src.scraper as scraper

def main():

    boop = scraper.scrape_websites()

    scraper.to_write_printer(boop)

if __name__ == "__main__":
    main()
