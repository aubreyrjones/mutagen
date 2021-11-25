%.pdf : %.odt ; 
	soffice --headless --convert-to pdf --outdir $(dir $?) $?
	sleep 0.25

define unite =
pdfunite $^ $@
endef

all: wizard.pdf sorcerer.pdf soma_master.pdf gm.pdf

# Define what's common to every player's playbook.
PCC = common/meta.pdf common/common.pdf

wizard.pdf: $(PCC) pcs/wizard.pdf ; $(unite)

sorcerer.pdf: $(PCC) pcs/sorcerer.pdf ; $(unite)

soma_master.pdf: $(PCC) pcs/soma_master.pdf ; $(unite)

gm.pdf: common/meta.pdf gm/gm.pdf common/common_gm.pdf ; $(unite)

clean:
	@find . -name \*.pdf -exec rm {} \;

-include private/all.mk
