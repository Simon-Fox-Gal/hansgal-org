var Hansgal = function(){
	
    return {
    	
        init : function() {
    		this.initFancybox();
        },
        
        initFancybox : function() {
        	$(document).ready(function() {
        		$('a.imagesItem').fancybox({
        			'speedIn'			: 600, 
        			'speedOut'			: 200, 
        			'overlayShow'		: true,
        			'hideOnContentClick': true
        		});
        	});

        },
        
        playAS : function(id, firstfilename) {
        	if ($('div#detail_'+id).is(":hidden")) {
        		$('div#detail_'+id).slideDown(600);
        		$('#audiosample_'+id).attr('class', 'audiosample active');
        		this.playASItem(firstfilename, id, 0);
        	} else {
        		$('div#detail_'+id).slideUp(600);
        		$('#audiosample_'+id).attr('class', 'audiosample');
        	}
        },
        
        playASItem : function(filename, id, index) {
	    	$.ajax({
	    		type: "POST",
	    		url: "/audiosamples/play/"+id+"/"+filename,
	    		success: function(result){
	    			if (result != '') {
	    				$('div#player').html(result);
	    			}
	        		$('span.nowplaying').html('');
	        		$('span#nowplaying_'+id+'_'+index).html('<i>Now playing...</i>');
	    		}
	    	});
        },
        
        showSmallPhoto : function(id) {
        	$('div#thumb'+id).css('display', 'block');
        },
        
        hideSmallPhoto : function(id) {
        	$('div#thumb'+id).css('display', 'none');
        },
        
        getRecordingInfo : function(id, params) {
	    	$.ajax({
	    		type: "POST",
	    		url: "/recordings/getalbuminfo/"+id,
	    		data: params,
	    		success: function(result){
	        		$('div#webshop').html(result);
	    		}
	    	});
        },
        
        order : function(ordercolumn, orderby) {
        	$('input#ordercolumn').val(ordercolumn);
        	$('input#orderby').val(orderby);
        	$('form#worksform').submit();
        },
        
        showBlock : function(id) {
        	if ($('div#'+id).is(":hidden")) {
        		$('div#'+id).slideDown(600);
        	} else {
        		$('div#'+id).slideUp(600);
        	}
        }
        
    };
    
}();

$(document).ready(function(){
	Hansgal.init();
});
