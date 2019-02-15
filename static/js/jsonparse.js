/**
 * 数组序列化为字符串
 * @param {Array} arr 待序列化的数组
 * @param {Number} [n=0] 缩进层次
 * @param {Boolean} [is_array=false] 是否是字符串
 * @returns {String} 数组转化后的字符串
 */
var $YCN={
	"object":"对象",
	"function":"函数",
	"array":"数组",
	"string":"字符串",
	"number":"数字",
	"boolean":"布尔值",
	"undefined":"未定义",
	"null":"空对象"
};

var _json_config={
	indent:"\t",
	br:"\r\n"
};

function a2s(arr,n,is_array){
	if(is_array!==false){is_array=true;}
	if(!n){n=0;}
	var str="["+_json_config.br;
	var tmp=[];
	for(var i=0;i<arr.length;i++){
		var ot=$Y(arr[i]);
		var rt=_json_config.indent.repeat(n);
		var suffix="\""+i+"\":";
		if(is_array){
			suffix="";
		}
		switch(ot){
			case "object":
				tmp.push(rt+suffix+o2s(arr[i],n+1));
				break;
			case "null":
				tmp.push(rt+suffix+"null");
				break;
			case "array":
				tmp.push(rt+suffix+a2s(arr[i],n+1,true));
				break;
			case "function":
			case "number":
				tmp.push(rt+suffix+arr[i].toString());
				break;
			case "undefined":
				tmp.push(rt+suffix+"undefined");
				break;
			case "regexp":
			case "boolean":
				tmp.push(rt+suffix+obj[i].toString());
				break;
			default:
				tmp.push(rt+suffix+"\""+arr[i].toString().replace(/"/g,"\\\"").replace(/\r/g,"\\r").replace(/\n/g,"\\n")+"\"");
		}
	}
	str+=tmp.join(","+_json_config.br);
	return str+_json_config.br+_json_config.indent.repeat(n-1)+"]";
}
/**
 * 对象转换为字符串
 * @param {JSONObject} obj 任意JS对象
 * @param {Number} [n=0] 缩进层次
 * @param {Boolean} [is_array=false] 是否是数组
 * @returns {String} 对象转换后的字符串
 */
function o2s(obj,n,is_array){
	if(!n){n=0;}
	var str="{"+_json_config.br;
	var tmp=[];
	for(var i in obj){
		var ot=$Y(obj[i]);
		var rt=_json_config.indent.repeat(n);
		var suffix="\""+i+"\":";
		if(is_array){
			suffix="";
		}
		switch(ot){
			case "object":
				tmp.push(rt+suffix+o2s(obj[i],n+1));
				break;
			case "null":
				tmp.push(rt+suffix+"null");
				break;
			case "array":
				tmp.push(rt+suffix+a2s(obj[i],n+1,true));
				break;
			case "function":
			case "number":
				tmp.push(rt+suffix+obj[i].toString());
				break;
			case "undefined":
				tmp.push(rt+suffix+"undefined");
				break;
			case "regexp":
			case "boolean":
				tmp.push(rt+suffix+obj[i].toString());
				break;
			default:
				tmp.push(rt+suffix+"\""+obj[i].toString().replace(/"/g,"\\\"").replace(/\r/g,"\\r").replace(/\n/g,"\\n")+"\"");
		}
	}
	str+=tmp.join(","+_json_config.br);
	return str+_json_config.br+_json_config.indent.repeat(n-1)+"}";
}