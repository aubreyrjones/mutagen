.SUFFIXES: .odt .pdf

.odt.pdf:
	soffice --headless --convert-to pdf --outdir $(dir $?) $?
	sleep 0.25

all: wizard sorcerer soma

wizard: common/meta.pdf common/common.pdf pcs/wizard.pdf
	pdfunite $? pdf_output/wizard_complete.pdf

sorcerer: common/meta.pdf common/common.pdf pcs/sorcerer.pdf
	pdfunite $? pdf_output/sorcerer_complete.pdf

soma: common/meta.pdf common/common.pdf pcs/soma_master.pdf
	pdfunite $? pdf_output/soma_master_complete.pdf



