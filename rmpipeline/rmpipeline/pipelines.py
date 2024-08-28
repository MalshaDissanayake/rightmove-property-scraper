import json
from datetime import datetime

class JsonWriterPipeline:
    def open_spider(self, spider):
        date_str = datetime.now().strftime('%Y-%m-%d')
        postcode_str = ''.join(spider.postcodes)
        self.file = open(f'rmpipeline_{postcode_str}_{date_str}.json', 'w')

    def close_spider(self, spider):
        if hasattr(self, 'file'):
            self.file.close()

    def process_item(self, item, spider):
        if hasattr(self, 'file'):
            line = json.dumps(dict(item)) + "\n"
            self.file.write(line)
        return item

 