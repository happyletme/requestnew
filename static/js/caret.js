var Caret={};
Caret.id=function(id){return document.getElementById(id);}
Caret.set= function(obj,start,end){
	if(typeof(obj)=="string"){
		obj=this.id(obj);
	}
   if(document.selection){
    if(obj.tagName=='TEXTAREA'){
     /*var i=obj.value.indexOf("\r",0);
     while(i!=-1&&i<end){
      end--;
      if(i<start){
       start--;
      }
      i=obj.value.indexOf("\r",i+1);
     }*/
    }
    var range=obj.createTextRange();
    range.collapse(true);
    range.moveStart('character',start);
    if(end!=undefined){
     range.moveEnd('character',end-start);
    }
    range.select();
   }else{
    obj.selectionStart=start;
    var sel_end=end==undefined?start:end;
    obj.selectionEnd=Math.min(sel_end,obj.value.length);
    obj.focus();
   }
	if(obj.scrollHeight>obj.clientHeight){
		var data=obj.value||obj.innerText||obj.textContent;
		//alert(data);
		var lines=data.match(/\n/g);
		//alert(lines);
	}
};