/**
 * Copyright (C) 2010, Tay Ray Chuan
 */

jQuery(function($) {
	var state = {
		running: false,
		reset: false,
		use_value: false
	};
	var field = $("input#field-hours");
	var stopwatch = $('<div></div>');
	stopwatch.append(StopwatchDisplay.display);
	stopwatch.append(StopwatchControls.controls);
	stopwatch.append($('<div class="clearer"></div>'));

	StopwatchControls.init(state);

	StopwatchControls.controls.bind("pause", StopwatchDisplay.pause_stopwatch);
	StopwatchControls.controls.bind("continue", StopwatchDisplay.continue_stopwatch);
	StopwatchControls.controls.bind("reset", StopwatchDisplay.reset_stopwatch);

	Toggler.init(state);

	Toggler.toggler.bind("show", function() { stopwatch.show("fast") });
	Toggler.toggler.bind("hide", function() {
		if (state.use_value)	field[0].value = StopwatchDisplay.get_hours();
	});
	Toggler.toggler.bind("hide", function() { stopwatch.hide("fast") });

	StopwatchControls.controls.bind("pause", Toggler.pause_handler);
	StopwatchControls.controls.bind("continue", Toggler.continue_handler);
	StopwatchControls.controls.bind("reset", Toggler.reset_handler);

	/* put toggler and stopwatch in a div, then put it below the hours <input>
	 * field. */
	field.after(
		$('<div></div>')
		.append(Toggler.toggler)
		.append($('<div class="clearer"></div>'))
		.append(stopwatch));

	/* initialize */
	StopwatchControls.controls.trigger("reset");
	Toggler.toggler.trigger("hide");
})
