SOFFICE = soffice
PDFUNITE = pdfunite

-include config.mk

%.pdf : %.odt ; 
	$(SOFFICE) --headless --convert-to pdf --outdir $(dir $?) $?
	@sleep 0.25

%.txt : %.odt ;
	$(SOFFICE) --headless --convert-to "txt:Text (encoded):UTF8" --outdir $(dir $?) $?
	@sleep 0.25

define unite =
$(PDFUNITE) $^ $@
endef

define txtcat =
cat $^ > $@
endef

all: wizard.pdf sorcerer.pdf soma_master.pdf gm.pdf

# Define what's common to every player's playbook.
pc_book = $(2): common/common.pdf $(1) common/meta.pdf ; $$(unite)
pc_text = $(2): common/common.txt $(1) common/meta.txt ; $$(txtcat)

# Build each PC playbook. Mind the spaces: $(call  pc_book,source_playbook_sections,output_name)
$(call pc_book,pcs/wizard.pdf,wizard.pdf)
$(call pc_book,pcs/sorcerer.pdf,sorcerer.pdf)
$(call pc_book,pcs/soma_master.pdf,soma_master.pdf)

$(call pc_text,pcs/sorcerer.txt,sorcerer.txt)

# Define what's common to every gm.
GM_Common = gm/gm.pdf gm/gm_common.pdf

# Build the generic GM playbook.
gm.pdf: $(GM_Common) ; $(unite)

clean:
	@find . -name \*.pdf -exec rm {} \;
	@find . -name \*.txt -exec rm {} \;


# If you're building a mutation, you can symlink your project
# directory to `mutation` and build playbooks with the same recipes as
# above.

-include mutation/all.mk
