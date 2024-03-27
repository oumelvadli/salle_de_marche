$(document).ready(function(){

    //-------------------------- cours ---------------------------//

    $("#openCoursModal").click(function(){
        $("#addCours").modal('show');
    });

    $("#openModifierCoursModal").click(function(){ // Correction ici
        $("#editCours").modal('show');
    });


    //-------------------------- bande ---------------------------//

    $("#openBandeModal").click(function(){
        $("#addBande").modal('show');
    });

    $("#openModifierBandeModal").click(function(){ // Correction ici
        $("#editBande").modal('show');
    });
    //-------------------------- importation ---------------------------//

    $("#openImportModal").click(function(){
        $("#import").modal('show');
    });

    $("#openVisualisationtModal").click(function(){
        $("#visualisation").modal('show');
    });

    //  annuler
    $("#addCours #annuler").click(function(){
        $("#addCours").modal('hide');
    });

    $("#addBande #annuler").click(function(){
        $("#addBande").modal('hide');
    });

    $("#import #annuler").click(function(){
        $("#import").modal('hide');
    });

    
});
setTimeout(function() {
    $('#success-alert').alert('close');
}, 3000);
function editCours(date, devise, cours, id) {
    document.getElementById("editCoursDate").value = date;
    document.getElementById("editCoursDevise").value = devise;
    document.getElementById("editCoursValue").value = cours;
    document.getElementById("formcours").action = "/update_cours/"+id;


    // Ouvrir le modal de modification
    $('#editCours').modal('show');
}
 //______________ ici ce deux lignes ont pour but de verifier que la date est valide _________________
 var dateActuelle = new Date().toISOString().split('T')[0];
 document.getElementById("bandeDate").setAttribute("max", dateActuelle);
 document.getElementById("coursDate").setAttribute("max", dateActuelle);
 document.getElementById("editCoursDate").setAttribute("max", dateActuelle);
 document.getElementById("editbandeDate").setAttribute("max", dateActuelle);
 //______________ fin _______________________

  function editBand(date, devise, Bid,Ask, id) {
      document.getElementById("editbandeDate").value = date;
      document.getElementById("editbandeDevise").value = devise;
      document.getElementById("editbandeBid").value = Bid;
      document.getElementById("editbandeAsk").value = Ask;
      document.getElementById("formbande").action = "/update_bande/"+id;


      // Ouvrir le modal de modification
      $('#editBande').modal('show');
  }
    var dateActuelle = new Date().toISOString().slice(0,10);
  
    document.getElementById('coursDate').addEventListener('change', function(){
        var selectedDate = this.value;
  
        if (selectedDate !== dateActuelle) {
            document.getElementById('dateError').textContent = "Attention : La date sélectionnée n'est pas la date actuelle.";
        } else {
            document.getElementById('dateError').textContent = "";
        }
    });
  
    document.getElementById('bandeDate').addEventListener('change', function(){
      var selectedDate = this.value;
  
      if (selectedDate !== dateActuelle) {
          document.getElementById('dateErrorBande').textContent = "Attention : La date sélectionnée n'est pas la date actuelle.";
      } else {
          document.getElementById('dateErrorBande').textContent = "";
      }
  });
  document.getElementById('editCoursDate').addEventListener('change', function(){
    var selectedDate = this.value;

    if (selectedDate !== dateActuelle) {
        document.getElementById('editDateError').textContent = "Attention : La date sélectionnée n'est pas la date actuelle.";
    } else {
        document.getElementById('editDateError').textContent = "";
    }
});
document.getElementById('editbandeDate').addEventListener('change', function(){
  var selectedDate = this.value;

  if (selectedDate !== dateActuelle) {
      document.getElementById('editDateErrorBande').textContent = "Attention : La date sélectionnée n'est pas la date actuelle.";
  } else {
      document.getElementById('editDateErrorBande').textContent = "";
  }
});


document.getElementById("import_btn").addEventListener("click", function (event) {
    console.log("Bouton d'importation cliqué !");
    event.preventDefault();

    // Vérification de l'extension de fichier
    var fileInput = document.getElementById("fileInput");
    var fileName = fileInput.value;
    console.log(fileName); // Débogage de la valeur de fileName

    // Vérifiez si le fichier a l'extension .xlsx
    if (!fileName.endsWith(".xlsx")) {
        alert("Le fichier doit être au format Excel (.xlsx)");
        return;
    }

    
    alert("importer avec succes");
});

    document.getElementById("dateForm").onsubmit = function() {
        var dateInput = document.getElementById("date_operation").value;
        var isValidDate = /^\d{2}\/\d{2}\/\d{4}$/.test(dateInput);
        if (!isValidDate) {
            alert("Format de date incorrect. Utilisez le format YYYY-MM-DD.");
            return false; // Empêche la soumission du formulaire si la date n'est pas valide
        }
    };
