import csv,json,random,datetime,pathlib
R=random.Random(42); root=pathlib.Path('data');
for d in ['synthetic','metadata','benchmarks']: (root/d).mkdir(parents=True,exist_ok=True)
def write(name,rows):
 with (root/'synthetic'/name).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
products=[dict(product_id=f'P{i:04}',name=f'Product {i}',category=R.choice(['Electronics','Packaging','Parts','Office']),unit_price=R.randint(100,5000),reorder_level=R.randint(20,100)) for i in range(1,501)]
suppliers=[dict(supplier_id=f'S{i:03}',name=f'Supplier {i}',lead_days=R.randint(2,21),reliability=round(R.uniform(.75,.99),3)) for i in range(1,51)]
inventory=[dict(product_id=p['product_id'],warehouse_id=f'W{R.randint(1,4)}',quantity=R.randint(0,350),reorder_level=p['reorder_level']) for p in products]
start=datetime.date(2024,10,1); end=datetime.date(2026,10,9)
def day():return (start+datetime.timedelta(days=R.randrange((end-start).days+1))).isoformat()
sales=[]
for i in range(1,10001):
 p=R.choice(products);q=R.randint(1,15);sales.append(dict(order_id=f'SO{i:06}',date=day(),product_id=p['product_id'],quantity=q,unit_price=p['unit_price'],revenue=q*p['unit_price'],region=R.choice(['North','South','East','West']),status=R.choice(['Delivered','Pending','Cancelled'])))
pos=[]
for i in range(1,1001):
 p=R.choice(products);q=R.randint(10,200);pos.append(dict(po_id=f'PO{i:05}',date=day(),supplier_id=R.choice(suppliers)['supplier_id'],product_id=p['product_id'],quantity=q,total_cost=q*round(p['unit_price']*.65),status=R.choice(['Draft','Pending Approval','Approved','Received'])))
deliveries=[dict(delivery_id=f'D{i:05}',order_id=R.choice(sales)['order_id'],date=day(),status=R.choice(['Delivered','In Transit','Delayed'])) for i in range(1,2501)]
finance=[dict(transaction_id=f'F{i:05}',date=day(),amount=R.randint(500,20000),type=R.choice(['Expense','Receipt','Supplier Payment'])) for i in range(1,3501)]
for name,rows in [('products.csv',products),('suppliers.csv',suppliers),('inventory.csv',inventory),('sales_orders.csv',sales),('purchase_orders.csv',pos),('deliveries.csv',deliveries),('finance.csv',finance)]:write(name,rows)
pages=[('DASHBOARD','Overview'),('INVENTORY','Inventory'),('SUPPLIERS','Suppliers'),('PROCUREMENT','Procurement'),('SALES','Sales'),('LOGISTICS','Logistics'),('FINANCE','Finance'),('ANALYTICS','Analytics'),('APPROVALS','Approvals'),('AGENT','Agent Activity')]
metadata={'pages':[{'page_id':'PAGE_'+id,'title':name,'route':'/'+name.lower().replace(' ','-'),'widgets':[{'widget_id':'GRID_'+id,'type':'grid'},{'widget_id':'CHART_'+id,'type':'chart'}],'filters':['date_range','status','region'],'api_id':'API_'+id} for id,name in pages]}
(root/'metadata'/'application_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
phrases=['Open {page}','Navigate to {page}','Show {page} dashboard','Where is {page}?','Take me to {page}']
with (root/'benchmarks'/'agent_prompts.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['prompt_id','utterance','intent','target_page_id','expected_route','split']);w.writeheader()
 for i in range(400):
  pid,name=pages[i%len(pages)];w.writerow(dict(prompt_id=f'Q{i+1:04}',utterance=phrases[(i//len(pages))%len(phrases)].format(page=name),intent='navigate',target_page_id='PAGE_'+pid,expected_route='/'+name.lower().replace(' ','-'),split='test' if i%5==0 else 'train'))
print('Generated 7 business CSVs, application_metadata.json, and 400 labelled navigation prompts in data/')
