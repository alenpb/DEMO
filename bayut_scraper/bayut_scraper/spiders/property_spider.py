import scrapy
class PropertySpider(scrapy.Spider):
    name = "property"
    start_urls = []
    for i in range(1, 61):
        url = f"https://www.bayut.eg/en/egypt/properties-for-sale/?page={i}"
        start_urls.append(url)
    def parse(self, response):
        links = response.css('a[href*="property/details"]::attr(href)').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_property)

    def parse_property(self, response):
        def clean(text):
            if text:
                return text.strip().replace("\n", "").replace("\t", "")
            return None
        def to_number(text):
            if text:
                text = text.replace(",", "").strip()
                try:
                    return int(text)
                except ValueError:
                    try:
                        return float(text)
                    except ValueError:
                        return None
            return None

        item = {}

        item["url"]=response.url
        item["id"]=response.url.split("-")[-1].replace(".html", "")
        item["reference_number"]=clean(response.xpath('//span[contains(text(),"Reference")]/following-sibling::span/text()').get())
        item["title"]=clean(response.css("h1::text").get())
        item["property_type"]=clean(response.xpath('//span[text()="Type"]/following-sibling::span/text()').get())

        price = response.css('span[aria-label="Price"]::text').get()
        if price:
            item["price"]=to_number(price.replace("EGP", "").replace(",", ""))
        else:
            item["price"]=None

        item["currency"]="EGP"
        item["location"]=clean(response.css('div[aria-label="Property header"]::text').get())
        item["bedrooms"]=to_number(response.css('span[aria-label="Beds"] span::text').re_first(r'(\d+)'))
        item["bathrooms"]=to_number(response.css('span[aria-label="Baths"] span::text').re_first(r'(\d+)'))
        item["furnished"]=clean(response.xpath('//span[text()="Furnishing"]/following-sibling::span/text()').get())
        item["completion_status"]=clean(response.css('span[aria-label="Completion status"]::text').get())
        item["ownership"]=clean(response.xpath('//span[text()="Ownership"]/following-sibling::span/text()').get())
        area=response.css('span[aria-label="Area"] span span::text').get()
        if area:
            parts=area.split()
            item["area"]=to_number(parts[0])
            item["area_unit"]=parts[1] if len(parts) > 1 else None
        else:
            item["area"]=None
            item["area_unit"]=None
        item["agent_name"]=clean(response.css('a[aria-label="Agent name"] h2::text').get())
        item["broker_name"]=clean(response.xpath('//a[@aria-label="Agent name"]/h2/text()').get())
        desc_raw=response.css('span._812d3f30 *::text').getall()
        item["description"]=" ".join([clean(d) for d in desc_raw if d]).strip()
        amenities=response.css('div.c20d971e span.c0327f5b::text').getall()
        item["amenities"]=[clean(a) for a in amenities if a]
        image_urls=response.css("img::attr(src)").getall()
        item["property_image_urls"]=[clean(url) for url in image_urls if url]
        yield item
