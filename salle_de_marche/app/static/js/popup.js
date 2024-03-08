$(document).ready(function(){
    $("#openCoursModal").click(function(){
        $("#addCours").modal('show');
    });

    $("#openBandeModal").click(function(){
        $("#addBande").modal('show');
    });

    //  annuler
    $("#addCours #annuler").click(function(){
        $("#addCours").modal('hide');
    });

    $("#addBande #annuler").click(function(){
        $("#addBande").modal('hide');
    });

    // validation
    $("#addCoursForm").submit(function(event) {
      var cours = $("#coursValue").val();

      if (isNaN(cours)) {
        $("#coursError").text("Le cours doivent être des entiers.");
        event.preventDefault();
      } else {
        $("#coursError").text("");
      }
    });

    $("#addBandeForm").submit(function(event) {
        // Validation du formulaire
        var max = $("#bandeMax").val();
        var min = $("#bandeMin").val();


        if (parseInt(min) >= parseInt(max)) {
            $("#minError").text("La valeur minimale doit être inférieure à la valeur maximale.");
            event.preventDefault();
        } else {
            $("#minError").text("");
        }

        if (isNaN(max) || isNaN(min)) {
          $("#minError").text("Les valeurs doivent être des entiers.");
          event.preventDefault();
        } else {
          $("#minError").text("");
        }

    });
});