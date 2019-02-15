var folded=false;
var indent="<span class='bgline'>┈┈</span>";
function $T(s){return s.replace(/^\s+|\s+$/,"");}
function $Y(obj){
	var ot=(typeof obj).lc();
	if(ot=="object"){
		if(obj){
			if(Object.prototype.toString.call(obj).toLowerCase().indexOf("array")!=-1){
				ot="array";
			}
			if(Object.prototype.toString.call(obj).toLowerCase().indexOf("regexp")!=-1){
				ot="regexp";
			}
		}else{
			ot="null";
		}
	}
	return ot;
}
function arr2str(arr,n,path,arrayflag){
	if(!n){n=1;}
	if(!path){path="";}
	var id=$R(8);
	var stat=["none",""];
	if(folded){stat=["","none"];}
	var str="<span id=\""+id+"_all\"><input type=\"button\" id=\""+id+"_fold\" style=\"display:"+stat[1]+";\" class=\"sbt_arr1\" onclick=\"btclick1('"+id+"',"+n+")\" /><input type=\"button\" id=\""+id+"_dot\" style=\"display:"+stat[0]+";\" class=\"sbt_arr2\" onclick=\"btclick2('"+id+"',"+n+")\" />[<span id=\""+id+"_desc\" style=\"padding:0px;display:"+stat[0]+";border:1px solid #000;background:#ff65BB\" onclick=\"btclick2('"+id+"',"+n+")\">&nbsp;收起的数组..&nbsp;</span><span id=\""+id+"\" style=\"display:"+stat[1]+";\">\r\n";
	var tmp=[];
	path=decodeURIComponent(path);
	for(var i=0;i<arr.length;i++){
		var ot=$Y(arr[i]);
		var tmppath=(path+"."+i);
		if(arrayflag){
			tmppath=path+"["+i+"]";
		}
		tmppath=encodeURIComponent(tmppath);
		var objstr=arr[i]?arr[i].toString():arr[i];
		var rt=indent.repeat(n)+"<input type=\"button\" class=\"sbt_normal\"  onclick=\"btclick3('"+tmppath+"','"+ot+"','"+objstr+"')\"></input>";
		var ckstr=rt+"\"<span onclick=\"btclick3('"+tmppath+"','"+ot+"','"+objstr+"')\" path=\""+tmppath+"\">"+i+"</span>\":";
		switch(ot){
			case "object":
				tmp.push(ckstr+obj2str(arr[i],n+1,tmppath));
				break;
			case "null":
				tmp.push(ckstr+"null");
				break;
			case "array":
				tmp.push(ckstr+arr2str(arr[i],n+1,tmppath,true));
				break;
			case "function":
			case "number":
				tmp.push(ckstr+arr[i].toString());
				break;
			case "undefined":
				tmp.push(ckstr+"undefined");
				break;
			case "boolean":
				tmp.push(ckstr+obj[i].toString());
				break;
			case "regexp":
				tmp.push(ckstr+""+arr[i].toString()+"");
				break;
			default:
				tmp.push(ckstr+"\""+arr[i].toString().replace(/"/g,"\\\"")+"\"");
		}
	}
	str+=tmp.join(",\r\n");
	return str+"\r\n"+indent.repeat(n-1)+"&nbsp;&nbsp;&nbsp;</span>]</span>";
}
function btclick1(id,n){
	T(id).hid();
	T(id+"_desc").show();
	T(id+"_fold").hid();
	T(id+"_dot").show();
	if(n==1){
		if($('#foldbutton')){
			$('#foldbutton').html("展开数据");
		}
	}
}
function btclick2 (id,n){
	T(id).show();
	T(id+"_desc").hid();
	T(id+"_fold").show();
	T(id+"_dot").hid();
	if(n==1){
		if($('#foldbutton')){
			$('#foldbutton').html("收起数据");
		}
	}
}

function btclick3 (path,type,value){
	path=decodeURIComponent(path);
	//双引变空单引串
	path=JSON.stringify(path).replace(/\\"/g,"\'");
	path=JSON.parse(path)
	$('#cpath').val(path);
	$('#ctype').val($YCN[type]||"未知");
	if(type=="array"){
		value="[未解析的数组]";
	}else if(type=="object"){
		value="[未解析的对象]";
	}
	//如果是bool值第一个字符需要大写
	if($('#ctype').val()=="布尔值"){
		value=value.substring(0,1).toUpperCase()+value.substring(1);
	}
	else if($('#ctype').val()=="空对象"){
		value="None";
	}
	$('#cvalue').val(value);
}
function obj2str(obj,n,path,arrayflag){
	if(!n){n=1;}
	if(!path){path="";}
	var id=$R(8);
	var stat=["none",""];
	if(folded){stat=["","none"];}
	var str="<span id=\""+id+"_all\"><input type=\"button\" id=\""+id+"_fold\" class=\"sbt_obj1\" style=\"display:"+stat[1]+";\" onclick=\"btclick1('"+id+"',"+n+")\" /><input type=\"button\" id=\""+id+"_dot\" style=\"display:"+stat[0]+";\" class=\"sbt_obj2\" onclick=\"btclick2('"+id+"',"+n+")\" />{<span id=\""+id+"_desc\" style=\"padding:0px;display:"+stat[0]+";border:1px solid #000;background:#66ccff\" onclick=\"btclick2('"+id+"',"+n+")\">&nbsp;收起的对象..&nbsp;</span><span id=\""+id+"\" style=\"display:"+stat[1]+";\">\r\n";
	var tmp=[];
	path=decodeURIComponent(path);
	for(var i in obj){
		var ot=$Y(obj[i]);
		var tmppath=(path+"."+i);
		if(/[^\w$]/.test(i)||/^[^a-zA-Z_$]/.test(i)){
			i=i.replace(/"/g,"\"");
			tmppath=path+"[\""+i+"\"]";
		}
		tmppath=encodeURIComponent(tmppath);
		var objstr=obj[i]?obj[i].toString():obj[i];
		var rt=indent.repeat(n)+"<input type=\"button\" class=\"sbt_normal\" onclick=\"btclick3('"+tmppath+"','"+ot+"','"+objstr+"')\"></input>";
		var ckstr=rt+"\"<span onclick=\"btclick3('"+tmppath+"','"+ot+"','"+objstr+"')\" path=\""+tmppath+"\">"+i+"</span>\":";
		switch(ot){
			case "object":
				tmp.push(ckstr+obj2str(obj[i],n+1,tmppath));
				break;
			case "null":
				tmp.push(ckstr+"null");
				break;
			case "array":
				tmp.push(ckstr+arr2str(obj[i],n+1,tmppath,true));
				break;
			case "function":
			case "number":
				tmp.push(ckstr+obj[i].toString());
				break;
			case "undefined":
				tmp.push(ckstr+"undefined");
				break;
			case "boolean":
				tmp.push(ckstr+obj[i].toString());
				break;
			case "regexp":
				tmp.push(ckstr+""+obj[i].toString()+"");
				break;
			default:
				tmp.push(ckstr+"\""+obj[i].toString().replace(/"/g,"\\\"")+"\"");
		}
	}
	str+=tmp.join(",\r\n");
	return str+"\r\n"+indent.repeat(n-1)+"&nbsp;&nbsp;&nbsp;</span>}</span>";
}
String.prototype.lc=function(){
	return this.toLowerCase();
}
String.prototype.uc=function(){
	return this.toUpperCase();
}
String.prototype["repeat"]=function(nn){
	if(!nn&&nn!==0) nn=1;
	var str="";
	for(var i=0;i<nn;i++){
		str+=this;
	}
	return str;
};
function $R(_n,type){
	var c={n:"0123456789",s:"abcdefghijklmnopqrstuvwxyz",b:"ABCDEFGHIJKLMNOPQRSTUVWXYZ",c:"!@#$%^&*()_+\\][}{:;'\",./?><~`"};
	var r="";
	var a="";
	if(type){
		type=type.split("");
		for(var i=0;i<type.length;i++){
			a+=c[type[i]];
		}
	}else{a=c.n+c.s+c.b;}
	for(var i=0;i<_n;i++){r+=a.charAt($R2(a.length));}
	return r;
}
function $R2(_n){return Math.floor(Math.random()*_n);}
function tips(str,n,end){
	if(str.length<n){
		return str;
	}else{
		return str.substring(0,n)+(end||" ..");
	}
}
function dquote (str){
	return str.replace(/"/g,"&quote;");
}