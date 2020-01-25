import requests
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

class Offer:
    def __init__(self, price, size, link, phone=None, publication_date=None):
        self.price = str(price)
        self.size = str(size)
        self.link = str(link)
        self.price_per_square_meter = str(round(float(price)/float(size),2))
        self.phone = str(phone)
        self.publication_date = str(publication_date)


class Scraper:
    def __init__(self, city, max_price=None, max_size=None):
        self.city = city
        self.max_price = max_price
        self.max_size = max_size
        self.offers = []

    def scrape_olx(self):
        url = r"https://www.olx.pl/nieruchomosci/mieszkania/wynajem/" + self.city + "/?search"
        if self.max_price is not None:
            url += r"[filter_float_price%3Ato]="
            url += str(self.max_price) + "&"
        if self.max_size is not None:
            url += r"[filter_float_m%3Ato]="
            url += str(self.max_size) + "&"
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        container = soup.find("table", {"class":"fixed offers breakword redesigned"})
        offers = container.findAllNext("tr", {"class":"wrap"})
        for offer in offers:
            price = offer.find("p", {"class":"price"}).text.replace(" ","")[:-3]
            try:
                link = offer.find("a", {"class":"marginright5 link linkWithHash detailsLink"})["href"]
            except TypeError:
                # Promoted offers have different class value
                link = offer.find("a", {"class":"marginright5 link linkWithHash detailsLinkPromoted"})["href"]
            offer_page = requests.get(link)
            offer_soup = BeautifulSoup(offer_page.text, "html.parser")
            container = offer_soup.find("div", {"class":"clr descriptioncontent marginbott20"})
            try:
                size = container.find_all_next("tr")[6].find("td",{"class":"value"}).text.replace(" ","").replace(",",".").strip()[:-2]
                self.offers.append(Offer(price=price, size=size, link=link))
            except Exception as e:
                print(e)

    def scrape_otodom(self):
        url = r"https://www.otodom.pl/wynajem/mieszkanie/" + self.city + "?search"
        if self.max_price is not None:
            url += r"&search%5Bfilter_float_price%3Ato%5D=" + str(self.max_price) + "&"
        if self.max_size is not None:
            url += r"&search%5Bfilter_float_m%3Ato%5D=" + str(self.max_size)

        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        container = soup.find("div", {"class":"col-md-content section-listing__row-content"})
        offers = container.findAllNext("article")
        for offer in offers:
            price = offer.find("li", {"class":"offer-item-price"}).text.replace(" ","").replace("zł","").replace("/mc","")
            size = offer.find("li", {"class":"hidden-xs offer-item-area"}).text.replace(" ","").replace(",",".").strip()[:-2]
            link = offer.find("a")["href"]
            self.offers.append(Offer(price=price, size=size, link=link))

    def export_to_file(self):
        with open("offers.csv", "w", encoding='utf-8') as f:
            f.write("Price, Size, Price per m2, Link, Description, Phone, Publication date")
            for offer in self.offers:
                f.write(offer.price + "," + offer.size + "," + offer.price_per_square_meter + "," +
                        offer.link + "," + offer.phone + "," + offer.publication_date)


def line_count(file):
    with open(file, 'r') as f:
        data=f.readlines()
    return len(data)

if __name__=="__main__":
    s = Scraper("Gliwice", max_price=1600, max_size=40)
    s.scrape_olx()
    s.scrape_otodom()
    s.export_to_file()
    plt.plot(range(line_count("offers.csv")-1), [o.price_per_square_meter for o in s.offers])
    plt.show()