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

    $("#addBandeForm").submit(function(event) {
        // Validation du formulaire
        var max = $("#bandeMax").val();
        var min = $("#bandeMin").val();


        if (min >= max) {
            $("#minError").text("La valeur minimale doit être inférieure à la valeur maximale.");
            event.preventDefault();
        } else {
            $("#minError").text("");
        }
    });
});