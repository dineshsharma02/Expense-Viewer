// console.log("search expense");
const searchIncomeField = document.querySelector("#searchIncomeField");
const tableIncomeOutput = document.querySelector(".table-income-output");
const appIncomeTable = document.querySelector(".app-income-table");
const itemNotFound = document.querySelector(".item-not-found")
const paginationContainer = document.querySelector(".pagination-container");
const tIncomeBody = document.querySelector(".table-income-body")
tableIncomeOutput.style.display='none';
itemNotFound.style.display='none';

searchIncomeField.addEventListener("keyup", (e) => {    
    const searchIncomeValue = e.target.value;
    
    if (searchIncomeValue.trim().length > 0) {
        itemNotFound.style.display="none"
        // tableOutput.innerHTML=""
        tIncomeBody.innerHTML="";
        paginationContainer.style.display='none'
        fetch("search-income", {
            body: JSON.stringify({ searchText: searchIncomeValue }),
            method: "POST",
        })
        .then((res) => res.json())
        .then((data) => {
            console.log("data", data);
            appIncomeTable.style.display='none'
            tableIncomeOutput.style.display='block'            
            if (data.length === 0){
                itemNotFound.style.display="block"
                tableIncomeOutput.style.display='none'
            }
            else{
                data.forEach((item) => {
                    
                    tIncomeBody.innerHTML += `
                <tr>
                    <td>${item.amount}</td>
                    <td>${item.source}</td>
                    <td>${item.description}</td>
                    <td>${item.date}</td>
                </tr>`;
                });
                
            }
        });
}
else{
    appIncomeTable.style.display='block';
    paginationContainer.style.display='block';
    tableIncomeOutput.style.display='none';
}

});
