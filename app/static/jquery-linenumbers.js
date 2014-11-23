(function($){
	$.fn.linenumbers = function(in_opts){
		// Settings and Defaults
		var opt = $.extend({
			col_width: '25px',
			col_height: '430px',
			start: 1,
			digits: 4.
		},in_opts);
		return this.each(function(){
			// Get some numbers sorted out for the CSS changes
			var new_textarea_width = (parseInt($(this).css('width'))-parseInt(opt.col_width))+'px';
			// Create the div and the new textarea and style it
			$(this).parent().before('<label for="code_input" style="float:left;"><textarea style="width:'+ opt.col_width + ';font-family:monospace;white-space:pre;overflow:hidden;resize:none !important;height:430px;text-align:right;" disabled="disabled" id="line_numbers"></textarea></label>');			// Edit the existing textarea's styles
			$(this).css({'width': '98%'});
			// Define a simple variable for the line-numbers box
			var lnbox = $(this).parent().parent().find('textarea[disabled="disabled"]');
			// Bind some actions to all sorts of events that may change it's contents
			$(this).bind('blur focus change keyup keydown',function(){
				// Break apart and regex the lines, everything to spaces sans linebreaks
				var lines = "\n"+$(this).val();
				lines = lines.match(/[^\n]*\n[^\n]*/gi);
				// declare output var
				var line_number_output='';
				// declare spacers and max_spacers vars, and set defaults
				var max_spacers = ''; var spacers = '';
				for(i=0;i<opt.digits;i++){
					max_spacers += ' ';
				}
				// Loop through and process each line
				$.each(lines,function(k,v){
					// Add a line if not blank
					if(k!=0){
						line_number_output += "\n";
					}
					// Determine the appropriate number of leading spaces
					lencheck = k+opt.start+'!';
					spacers = max_spacers.substr(lencheck.length-1);
					// Add the line, trimmed and with out line number, to the output variable
					if ((k + opt.start) < 1000) {
						line_number_output += (k+opt.start)+':';
					}
					else {
						line_number_output += '...'
					}
				});
				// Give the text area out modified content.
				$(lnbox).val(line_number_output);
				// Change scroll position as they type, makes sure they stay in sync
			    $(lnbox).scrollTop($(this).scrollTop());
			})
			// Lock scrolling together, for mouse-wheel scrolling 
			$(this).scroll(function(){
			    $(lnbox).scrollTop($(this).scrollTop());
			});
			// Fire it off once to get things started
			$(this).trigger('keyup');
		});
	};
})(jQuery);
