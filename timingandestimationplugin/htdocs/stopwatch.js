/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

$(document).ready(function() {
	var state = {
		running: false,
		reset: false,
		use_value: false
	};
	var field = $("input#field-hours");
	var stopwatch = $('<div></div>');

	stopwatch.append(StopwatchDisplay.display);

	StopwatchControls.init(state, stopwatch);

	StopwatchControls.controls.bind("pause", StopwatchDisplay.pause_stopwatch);
	StopwatchControls.controls.bind("continue", StopwatchDisplay.continue_stopwatch);
	StopwatchControls.controls.bind("reset", StopwatchDisplay.reset_stopwatch);

	Toggler.init(state, field[0]);

	Toggler.toggler.bind("show", function() { stopwatch.show("fast") });
	Toggler.toggler.bind("hide", function() { stopwatch.hide("fast") });

	StopwatchControls.btn_flow.click(Toggler.btn_flow_click);
	StopwatchControls.btn_reset.click(Toggler.btn_reset_click);

	/* put toggler and stopwatch in a div, then put it below the hours <input>
	 * field. */
	field.after(
		$('<div></div>')
		.append(Toggler.toggler)
		.append(stopwatch));

	/* initialize */
	StopwatchControls.btn_reset.click();
	Toggler.toggler.click();
})
