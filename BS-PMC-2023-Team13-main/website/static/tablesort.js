
function sortTableByColumn(table, col, asc = true){
    const dirModifier = asc ? 1 : -1;
    const tBody = table.tBodies[0];
    const rows = Array.from(tBody.querySelectorAll("tr"));

    // Sort each row //
    const sortedRows = rows.sort((a,b) => {
        const aColText = a.querySelector(`td:nth-child(${ col + 1})`).textContent.trim();
        const bColText = b.querySelector(`td:nth-child( ${ col + 1})`).textContent.trim();
        
        return aColText > bColText ? (1*dirModifier) : (-1* dirModifier);
    });

    // Remove all existing TRs from the table //
    while (tBody.firstChild){
        tBody.removeChild(tBody.firstChild);
    }

    // Re-add the newly sorted rows //
    tBody.append(...sortedRows);

    // Remember how the columm is currently sorted //
    table.querySelectorAll("th").forEach(th => th.classList.remove("th-sort-asc", "th-sort-desc"));
    table.querySelector(`th:nth-child(${ col +1})`).classList.toggle("th-sort-asc", asc);
    table.querySelector(`th:nth-child(${ col +1})`).classList.toggle("th-sort-desc", !asc);

}

document.querySelectorAll(".table-sortable th").forEach(headerCell => {
    headerCell.addEventListener("click", () => {
        const tableElement = headerCell.parentElement.parentElement.parentElement;
        const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
        const currentIsAsc = headerCell.classList.contains("th-sort-asc");

        sortTableByColumn(tableElement, headerIndex, !currentIsAsc);
    });
});