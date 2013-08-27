// http://stackoverflow.com/questions/1038746/equivalent-of-string-format-in-jquery
String.prototype.format = function () {
  var args = arguments;
  return this.replace(/\{(\d+)\}/g, function (m, n) { return args[n]; });
};

// StackOverflow (source unknown)
// Escape strings for use as JQuery selectors
function jqSelector(str) {
  return str.replace(/([;&,\.\+\*\~':"\!\^#$%@\[\]\(\)=>\|])/g, '\\$1');
}

function create_dropdown(menu, file, path, collection_id, type) {
	// For string formats:
	// Arg 0 is file, 1 path, 2 collection_id
	if (type === "directory") {
		var to_replace = '<ul class="dropdown-menu my-dropdown" onclick="return false;"><li><a href="javascript:void(0)" onclick="create_file({0}, {1}, {2});"><i class="icon-plus"></i> Create File Here</a></li><li><a href="javascript:void(0)" onclick="create_directory({0}, {1}, {2});"><i class="icon-plus"></i> Create Directory Here</a></li><li><a href="javascript:void(0)" onclick="upload_file({0}, {1}, {2});"><i class="icon-arrow-up"></i> Upload File Here</a></li><li><a href="javascript:void(0)" onclick="delete_directory({0}, {1}, {2});"><i class="icon-remove-sign"></i> Delete Directory</a></li><li><a href="javascript:void(0)" onclick="restore_file({0}, {1}, {2});"><i class="icon-repeat"></i> Restore To Original</a></li></ul>';
	}
	if (type === "collection") {
		var to_replace = '<ul class="dropdown-menu my-dropdown" onclick="return false;"><li><a href="javascript:void(0)" onclick="create_file({0}, {1}, {2});"><i class="icon-plus"></i> Create File Here</a></li><li><a href="javascript:void(0)" onclick="create_directory({0}, {1}, {2});"><i class="icon-plus"></i> Create Directory Here</a></li><li><a href="javascript:void(0)" onclick="upload_file({0}, {1}, {2});"><i class="icon-arrow-up"></i> Upload File Here</a></li><li><a href="javascript:void(0)" onclick="restore_file({0}, {1}, {2});"><i class="icon-repeat"></i> Restore To Original</a></li></ul>';
	}
	if (type === "file") {
		var to_replace = '<ul class="dropdown-menu my-dropdown" onclick="return false;"><li><a href="javascript:void(0)" onclick="delete_file({0}, {1}, {2});"><i class="icon-remove-sign"></i> Delete File</a></li><li><a href="javascript:void(0)" onclick="restore_file({0}, {1}, {2});"><i class="icon-repeat"></i> Restore To Original</a></li></ul>';
	}
	// Ensure only one dropdown exists at once
	clear_dropdowns();
	$(menu).after(to_replace.format("'"+file+"'", "'" + path + "'", collection_id));
}

// Spawn dropdown menu on label "label" in file browser
function spawn_dropdown_on(label, file, path, collection_id, type) {
  var whee = $(label).find('> .dropdown > .dropdown-toggle').get(0);
  create_dropdown(whee, file, path, collection_id, type);
  return false;
}

// Clear all menus on screen
function clear_dropdowns() {
  $(".my-dropdown").each(function(index) {
    this.style.display = "none";
  });
}
