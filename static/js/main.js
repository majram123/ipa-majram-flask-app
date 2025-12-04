// coding by oualid belaid ;
// 2023-02-04

// Sidebar functions
window.openSidebar = function() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar && overlay) {
        sidebar.classList.add('active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
};

window.closeSidebar = function() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebar && overlay) {
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
};

// Close sidebar when clicking on a link
$(document).ready(function() {
    $('.sidebar-menu a').click(function() {
        setTimeout(function() {
            window.closeSidebar();
        }, 300);
    });
});

//Define the number of elements to display
var nbr_ele_show = 10;


//Main function to show and hide the elements
function show_element ()
{
    //Loop over each element and show or hide according to the nbr_ele_show variable
    $.each( $( ".list .child" ), function ( indexInArray, valueOfElement )
    {

        //If the index matches the nbr_ele_show variable then display the elements
        if ( indexInArray < nbr_ele_show )
        {
            $( valueOfElement ).show( 200 );
        }
        //Otherwise hide the element
        else
        {
            $( valueOfElement ).hide();
        }
    } );
};

//When the document is ready call the show_element function
$( "nav li a" ).each( function ()
{
    var pageUrl = window.location.href.split( /[?#]/ )[ 0 ];
    console.log( pageUrl );
    if ( this.href == pageUrl )
    {
        $( this ).addClass( "active" );
    }
} );
$( document ).ready( function ()
{
    show_element();

    //On click show 10 more elements in the list
    $( ".more" ).click( function ( e )
    {
        e.preventDefault();
        nbr_ele_show += 10;
        show_element();
    } );

    //When the #show-desc button is clicked add a class to the element and animate it to show the description
    $( ".child #show-desc" ).click( function ( e )
    {
        e.preventDefault();
        $( this ).closest( ".child" ).addClass( "active" );
        $( this ).closest( ".child" ).siblings().removeClass( "active" );
        let x = ( $( this ).parent().height() + 70 ) + "px";
        $( this ).closest( ".child" ).animate( {
            minHeight: x
        }, 500 );
        //Hide the siblings
        $( this ).closest( ".child" ).siblings( ".child" ).animate( {
            minHeight: "60px",
            height: "60px"
        }, 500 );
    } );

    //When the #hide-desc button is clicked remove the class and animate the element to hide the description
    $( ".child #hide-desc" ).click( function ( e )
    {
        e.preventDefault();
        $( this ).closest( ".child" ).removeClass( "active" );

        $( this ).closest( ".child" ).animate( {
            minHeight: "60px",
            height: "60px"
        }, 500 );
    } );
} );
