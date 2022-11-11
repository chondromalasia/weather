import src.scraper as scraper
import src.database as database

def update_highs(city):
    start_date = database.most_recent_high_date(city)
    final_url = scraper.format_url(city, start_date, "today")
    df = scraper.date_dataframe(final_url)
    to_write = database.prep_to_write(df, "CHI", start_date)
    database.write_high_temps(to_write)


def main():

    loop = True

    while loop:
        boop = scraper.scrape_websites()

        scraper.to_write_printer(boop)

        is_done = input("type y if this looks correct")

        if is_done == 'y':
            loop = False

    print("Database Init")
    database.database_init()

    print("Writing Rows")
    database.write_rows(boop)

    print("Updating Highs")
    update_highs("CHI")
    update_highs("NYC")

if __name__ == "__main__":
    main()
