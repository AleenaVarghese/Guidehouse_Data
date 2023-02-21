from PyPDF2 import PdfFileWriter, PdfFileReader
			
def split_pdf_to_two(filename,page_number):
	pdf_reader = PdfFileReader(open(filename, "rb"))
	try:
		#The assert keyword lets you test if a condition in your code returns True, if not, the program will raise an AssertionError.
		assert page_number < pdf_reader.numPages
		pdf_writer2 = PdfFileWriter()
		
		print("pdf_reader.getNumPages()",pdf_reader.getNumPages())
		for page in range(page_number-1,pdf_reader.getNumPages()+1):
			print(page)
			pdf_writer2.addPage(pdf_reader.getPage(page))

		with open("part2.pdf", 'wb') as file2:
			pdf_writer2.write(file2)

	except AssertionError as e:
		print("Error: The PDF you are splitting has less pages than you want to split!")	
		

split_pdf_to_two("Umass.pdf",50000)