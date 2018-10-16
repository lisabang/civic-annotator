widgetGenerators['civic'] = {
	'variant': {
		'width': 280, 
		'height': 80, 
		'function': function (div, row, tabName) {
			addInfoLine(div, row, 'Clinical actionability score', 'civic__clinical_a_score', tabName);
			var link = infomgr.getRowValue(tabName, row, 'civic__link');
			if (link == null) {
				link = 'None';
				addInfoLineText(div, 'Link', link);
			} else {
				addInfoLineLink(div, 'Link', link, link, -1);
			}
			addInfoLine(div, row, 'Description', 'civic__description', tabName);
			addInfoLine(div, row, 'Diseases', 'civic__diseases', tabName);
		}
	}
}