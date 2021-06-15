<script>

    window.addEventListener("load", function() {
        document.getElementById("search").addEventListener("keypress", search_handler);
        document.getElementById("search-button").addEventListener("click", run_search);
    });

    function search_handler(e) {
        if(e.key === "Enter"){
            e.preventDefault();
            run_search();
            return false;
        }
    }

    function run_search() {
        var search_val = document.getElementById("search").value;
        if(search_val == "") { return; }

        const xhr = new XMLHttpRequest();

        xhr.onload = function() {
            if (this.status === 200) {

                var search_data = JSON.parse(this.response);
                document.getElementById("result-container").innerHTML = '';

                // add each matching result to the page
                for (var i = 0; i < search_data.length; i++) {
                    create_search_result(search_data[i]);
                }

            } else {
                document.getElementById("result-container").innerHTML = "<span style='color:red'>An error occurred</span";
            }
        }

        xhr.open("GET", "/search_knowledge.php?search="+encodeURI(search_val));
        xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
        xhr.send();
    }

    function create_search_result(data) {
        var container = document.getElementById("result-container");
        var result = document.createElement("div");
        result.style.padding = "1em 0px";
        result.style.borderTop = "1px solid #888888";
        result.style.borderBottom = "1px solid #888888";

        var title = document.createElement("h2");
        var a = document.createElement("a");
        a.href = data.url;
        a.innerText = data.name;

        var p = document.createElement("p");
        p.style.maxHeight = "15em";
        p.style.overflow = "hidden";
        p.style.backgroundColor = "#DDDDDD"
        p.style.opacity = 0.5;
        p.innerHTML = data.content;


        title.appendChild(a);
        result.appendChild(title);
        result.appendChild(p);

        container.appendChild(result);
    }
</script>

<form id="search-form" action="#">
  <p>
    <input id="search" size="30" type="text">&ensp;
    <input id="search-button" type="button" value="Search">
  </p>
</form>

<div id="result-container"></div>