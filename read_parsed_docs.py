import pickle

with open(file='parsed_docs_dict1.pickle', mode='rb') as f:
    parsed_results_with_pdfplumber=pickle.load(f)

print(len(parsed_results_with_pdfplumber))
print(type(parsed_results_with_pdfplumber))
print(type(parsed_results_with_pdfplumber.values()))
print(parsed_results_with_pdfplumber.keys())
print(parsed_results_with_pdfplumber['FWG'][2])
print("="*70)

with open(file='parsed_docs_dict2.pickle', mode='rb') as f:
    parsed_results_with_pdfminer=pickle.load(f)

print(len(parsed_results_with_pdfminer))
print(type(parsed_results_with_pdfminer))
print(type(parsed_results_with_pdfminer.values()))
print(parsed_results_with_pdfminer.keys())
print(parsed_results_with_pdfminer['FWG'][2])


