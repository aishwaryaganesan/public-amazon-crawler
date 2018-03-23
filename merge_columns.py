import pickle
import sys
from walmart_crawler import ProductRecord
reload(sys)
sys.setdefaultencoding('utf8')

properties = [
                ('Average Battery Life', 'Average Battery Life (in hours)', 'Battery Life'),
                ('Brand', 'Brand Name','Manufacturer'),
                ('Processor (CPU) Manufacturer', 'Processor Brand', 'Processor Series', 'Processor', 'Processor Type', 'Processor Core Type', 'CPU Model','Procesor', 'CPU'),
                ('Processor Speed', 'CPU Speed'),
                ('Color','Color Category'),
                ('RAM Size', 'Computer Memory Size', 'RAM Memory', 'Maximum RAM Supported'),
                
                ('Screen Size', 'Display Size'),
                ('Display Resolution', 'Screen Resolution', 'Display Resolution Maximum'),
                ('Hard Disk Size', 'Hard-Drive Size', 'Hard Drive Capacity', 'Flash Memory Installed Size', 'Flash Memory Size',  'Storage'),
                ('Item Dimensions', 'Item Dimensions  L x W x H', 'Package Dimensions', 'Product Dimensions', 'Assembled Product Dimensions (L x W x H)', 'Dimension', 'Dimensions'),
                ('Item Weight', 'Weight', 'Weight (Lbs)', 'Assembled Product Weight'),
                ('Operating System', 'Operation System'),
                ('Laptop Computer Type', 'Hardware Platform'),
                ('Wireless Type', 'Wireless Compatibility', 'Wireless Compability', 'Wireless Technology', 'Wireless'),
                ('Manufacturer Part Number', 'manufacturer_part_number', 'Item model number', 'Manufacturer Part Number'),
                ('Model', 'Series'),
                ('Processor Count'),
                ]
def main():
    brand='walmart'
    filename = 'data/' + brand + '_products.p'
    data = pickle.load(open(filename,'rb'))

    matching_attributes = [
                            ('Average Battery Life','Average Battery Life (in hours)'),
                            ('Battery Cell Type', 'Battery Type'),
                            ('Brand', 'Manufacturer'),
                            ('Computer Memory Size', 'Ram Size'),
                            ('Computer Memory Speed', 'Memory Speed'),
                            ('Item Dimensions','Item Dimensions L x W x H')
                        ]

    # Properties that all products will have. Each word in each tuple refers to the same real world entity as the rest of the words in the tuple.

    for item in data:
        new = {}
        used = []
        for key in sorted(item.properties.keys()):
            v, prop = key_in_props(key)
            # If the property has not been seen yet and is a property in properties
            if v >= 0 and v not in used:
                new[prop.lower()] = ''.join([c for c in list(item.properties[key].replace(',','').replace('\\','').replace('\n','')) if ord(c) < 128])
                used.append(v)

        # Add empty values for properties not seen.
        for i in range(len(properties)):
            if i not in used:
                prop_list = properties[i]
                if type(prop_list) is tuple:
                    new[prop_list[0]] = '-'
                elif type(prop_list) is str:
                    new[prop_list] = '-'

        # Overwrite properties
        item.properties = new
    
    pickle.dump(data, open(filename,'wb'))

    # Write csv
    with open('data/'+brand+'_products.csv', 'w') as f:
        keys = ','.join(sorted(data[0].properties.keys())) + '\n'
        print 'product title,price,' + keys
        f.write('product title,price,' + keys)
        for item in data:
            values = ','.join([item.properties[key] for key in sorted(item.properties.keys())]) + '\n'
            try:
                #print(str(item.title[0]).replace(',' , '') + ',' + str(item.price) + ',' + values)
                f.write(str(item.title).replace(',' , '').replace('\\','').replace('\n','') + ',' + str(item.price).replace(',' , '').replace('\\','').replace('\n','') + ',' + values)
            except Exception as e:
                pass


    # for item in data:
    #     for prop in properties:
    #         found = []
    #         if type(prop) is tuple:
    #             for prop_variation in prop:
    #                 prop_variation = prop_variation.lower()
    #                 for key in item.properties.keys():
    #                     key = key.strip()
    #                     if prop_variation in key.lower() and abs(len(prop_variation)-len(key)) <= 2:
    #                         # print(prop_variation, item.properties[key], 'tup')
    #                         found.append((prop_variation,item.properties[key]))
    #         if len(found) > 1:
    #             print(found)
    #             print(item.properties)
    #         elif type(prop) is str:
    #             prop = prop.lower()
    #             for key in item.properties.keys():
    #                 key = key.strip()
    #                 if prop in key.lower() and abs(len(prop)-len(key)) <= 2:
    #                     print(prop, item.properties[key], 'str')
    #     print(item.properties)
    #     print()
    
    # q = 'Computer Memory Type'
    # for item in data:
    #     try:
    #         for key in item.properties.keys():
    #             if q.lower() in key.lower() and abs(len(q) - len(key)) <= 10:
    #                 print(key)
    #                 print(item.properties[key])
    #     except:
    #         pass


    # props = []
    # for item in data:
    #     for key in item.properties.keys():
    #         if key not in props:
    #             props.append(key)

    # for p in sorted(props):
    #     print(p)

# Determines if the key is in properties, and if so, the index.
def key_in_props(key):
    key = key.lower()
    for i, prop_list in enumerate(properties):
        if type(prop_list) is tuple:
            for prop in prop_list:
                prop = prop.lower()
                if (key in prop or prop in key) and abs(len(prop)-len(key)) <= 2:
                    return i, prop_list[0]
        elif type(prop_list) is str:
            prop = prop_list.lower()
            if (key in prop or prop in key) and abs(len(prop)-len(key)) <= 2:
                    return i, prop
    return -1, None

if __name__ == '__main__':
    main()
