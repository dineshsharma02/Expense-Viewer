// console.log("search expense");
const searchField = document.querySelector("#searchField");
const tableOutput = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const itemNotFound = document.querySelector(".item-not-found")
const paginationContainer = document.querySelector(".pagination-container");
const tbody = document.querySelector(".table-body")
tableOutput.style.display='none';
itemNotFound.style.display='none';

searchField.addEventListener("keyup", (e) => {    
    const searchValue = e.target.value;
    
    if (searchValue.trim().length > 0) {
        itemNotFound.style.display="none"
        // tableOutput.innerHTML=""
        tbody.innerHTML="";
        paginationContainer.style.display='none'
        fetch("/search-expenses", {
            body: JSON.stringify({ searchText: searchValue }),
            method: "POST",
        })
        .then((res) => res.json())
        .then((data) => {
            console.log("data", data);
            appTable.style.display='none'
            tableOutput.style.display='block'
            
            if (data.length === 0){
                itemNotFound.style.display="block"
                tableOutput.style.display='none'
            }
            else{
                data.forEach((item) => {
                    
                    tbody.innerHTML += `
                <tr>
                    <td>${item.amount}</td>
                    <td>${item.category}</td>
                    <td>${item.description}</td>
                    <td>${item.date}</td>
                </tr>`;
                });
                
            }
        });
}
else{
    appTable.style.display='block';
    paginationContainer.style.display='block';
    tableOutput.style.display='none';
}

});
