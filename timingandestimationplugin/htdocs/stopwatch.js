/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

$(document).ready(function() {
	var toggler, stopwatch;
	
	stopwatch = $('<div>stopwatch goes here</div>');
	toggler = $('<div>Show stopwatch</div>')
		.append(stopwatch);
	toggler.click(function() {
		stopwatch.toggle("fast");
	});
	
	$("input#field-hours").after(toggler);
})
