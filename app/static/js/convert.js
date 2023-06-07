      // Quick and simple export target #table_id into a csv
function downloadTableAsCsv(tableId, name, separator = ',') {
    // Select rows from tableId
    var rows = document.querySelectorAll('table#' + tableId + ' tr');
    // Construct csv
    var csv = [];
    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll('td, th');
        for (var j = 0; j < cols.length; j++) {
            // Clean innertext to remove multiple spaces and jumpline (break csv)
            var data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' ')
            // Escape double-quote with double-double-quote (see https://stackoverflow.com/questions/17808511/properly-escape-a-double-quote-in-csv)
            data = data.replace(/"/g, '""');
            // Push escaped string
            row.push('"' + data + '"');
        }
        csv.push(row.join(separator));
    }
    var csv_string = csv.join('\n');
    let date_str = new Date().toLocaleString().replace(/ /g, '_').replace(/\//g, '').replace(/:/g, '').replace(/,/g, '')
    // Download it
    var link = document.createElement('a');
    link.href = 'data:text/csv;charset=utf-8,' + encodeURI(csv_string);
    link.target = '_blank';
    link.download = name + '_' + date_str + '.csv';
    link.click();
    document.body.removeChild(link);
}