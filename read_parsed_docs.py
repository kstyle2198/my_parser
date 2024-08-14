import pickle
from pprint import pprint

with open(file='parsed_docs_dict.pickle', mode='rb') as f:
    parsed_results_with_pdfplumber=pickle.load(f)

print(f"파싱문서개수: {len(parsed_results_with_pdfplumber)}")
print(type(parsed_results_with_pdfplumber))
print(parsed_results_with_pdfplumber.keys())
샘플문서명 = list(parsed_results_with_pdfplumber.keys())[0]
print(샘플문서명)
print(parsed_results_with_pdfplumber[샘플문서명][0])


