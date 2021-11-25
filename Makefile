.SUFFIXES: .odt .pdf

.odt.pdf:
	soffice --headless --convert-to pdf --outdir $(dir $?) $?
	sleep 0.25

#.pdf.pdf:
#	pdfunite $^ $@

all: wizard sorcerer soma

pdf_output/pcs_common.pdf: common/meta.pdf common/common.pdf
	pdfunite $^ $@

wizard: pdf_output/pcs_common.pdf  pcs/wizard.pdf
	pdfunite $? pdf_output/wizard_complete.pdf

sorcerer: pdf_output/pcs_common.pdf pcs/sorcerer.pdf
	pdfunite $? pdf_output/sorcerer_complete.pdf

soma: pdf_output/pcs_common.pdf pcs/soma_master.pdf
	pdfunite $? pdf_output/soma_master_complete.pdf

clean:
	find . -name *.pdf -exec rm {} \;

