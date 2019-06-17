//点击子复选框,全选框 选中、取消
//allCheckId --总勾选框Id
/*
allCheckId ---总勾选框Id
allCheckType ---总勾选框类别
checkClass ---子勾选框的class
 */
function setAll(allCheckId,allCheckType,checkClass){
    if(!$("."+checkClass).checked){
        $("#"+allCheckId).prop("checked",false); // 子复选框某个不选择，全选也被取消
    }
    var choicelength=$("input[type='"+allCheckType+"'][class="+checkClass+"]").length;
    var choiceselect=$("input[type='"+allCheckType+"'][class="+checkClass+"]:checked").length;

    if(choicelength==choiceselect && choicelength){
        $("#"+allCheckId).prop("checked",true);   // 子复选框全部部被选择，全选也被选择；1.对于HTML元素我们自己自定义的DOM属性，在处理时，使用attr方法；2.对于HTML元素本身就带有的固有属性，在处理时，使用prop方法。
    }
}


// 根据返回值去勾选对应列
/*
checked_ids ---全局变量
tableId ---表格id
allCheckId ---总勾选框Id
allCheckType ---总勾选框类别
checkClass ---子勾选框的class
 */
function check(tableId,allCheckId,allCheckType,checkClass){
    checked_ids=checked_ids.split(",");
    //当前页的列id
    $("#"+tableId).find(":"+allCheckType+"."+checkClass).each(function(){
        id=$(this).parent().next().text();
        if (id != "") {
            if (checked_ids.includes(String(id))){
                $(this).attr("checked", true);
            }
        }
    });
    //全选
    setAll(allCheckId,allCheckType,checkClass);
}

//根据当前页的勾选变化改变checked_ids值
/*
checked_ids ---返回的id集合，','隔开的字符串
tableId ---表格id
allCheckType ---总勾选框类别
checkClass ---子勾选框的class
 */
function change_checked_ids(checked_ids,tableId,allCheckType,checkClass){
    //当前页的列id
    $("#"+tableId).find(":"+allCheckType+"."+checkClass).each(function(){
        id=$(this).parent().next().text();
        if (id != "") {
            //选中则判断数组是否存在，不存在则入栈
            if ($(this).is(":checked")){
                if (!checked_ids.includes(String(id))){
                    checked_ids.push(String(id));
                }
            }
            //未选中则判断数组是否存在，存在则出栈
            else{
                if (checked_ids.includes(String(id))){
                    checked_ids = $.grep(checked_ids, function(value) {
                        return value != String(id);
                    });
                }
            }
        }
    });
    return checked_ids
}

//点击全选按钮勾选子节点操作
/*
allCheckId ---总勾选框Id
checkName ---子勾选框的名字
 */
function checkAll(allCheckId,checkName){
    var allcheck=document.getElementById(allCheckId);
    var choice=document.getElementsByName(checkName);
    for(var i=0;i<choice.length;i++){
        choice[i].checked=allcheck.checked;
    }
}

//删除
/*
btn --删除按钮id
ipt --输入框存选中列的id
tableId ---表格id
allCheckType ---总勾选框类别
checkClass ---子勾选框的class
alertId ---前端提示框ID
 */
function del(btn,ipt,tableId,allCheckType,checkClass,alertId){
    $("#"+btn).click(function(){
        //调整被勾选的值
        checked_ids=change_checked_ids(checked_ids,tableId,allCheckType,checkClass);
        $("#myAlert").css("display","none");
        $("#myAlert1").css("display","none");
        $("#myAlert2").css("display","none");
        if (checked_ids.length<=1){
            $("#"+alertId).css("display","inherit");
            return false;
        }
        else{
            $("#"+ipt).val(checked_ids);
        }
    });
}

//判断提交的表单是否错误
/*
isRepeat --返回值标志
RepeatMessage --返回值内容
tipModalLabel ---提示模态框lable的id
tipModal ---提示模态框id
 */
function funisError(tipModalLabel,tipModal){
    if (code<0 || code>0){
        $("#"+tipModalLabel).text(codeMessage);
        $('#'+tipModal).modal("show");
    }
}

//icon提示
/*
tableId --表单Id
icon --icon的类
 */
function tip(tableId,icon){
    $("#"+tableId).find("."+icon).each(function(){
        $(this).mouseover(function(){
            $(this).tooltip;
         });
    });
}

//生成脚本
/*
btn --生成脚本按钮id
ipt --输入框存选中列的id
tableId ---表格id
allCheckType ---总勾选框类别
checkClass ---子勾选框的class
alertId ---前端提示框ID
 */
function makepy(btn,ipt,tableId,allCheckType,checkClass,alertId){
    del(btn,ipt,tableId,allCheckType,checkClass,alertId);
}

//批量修改appname
/*
btn --批量修改appname按钮id
ipt --输入框存选中列的id
tableId ---表格id
allCheckType ---总勾选框类别
checkClass ---子勾选框的class
alertId ---前端提示框ID
 */
function editAppname(btn,ipt,tableId,allCheckType,checkClass,alertId){
    del(btn,ipt,tableId,allCheckType,checkClass,alertId);
}

//修改变成带输入框的select框
/*
selectClass --select一部分类
*/
function changeSelect(selectClass){
    $('.'+selectClass).selectpicker({
        'selectedText': 'cat'
    });
}

//列表数据一旦超过多少个字符串就只显示，多少个字符串+...
/*
tableId ---表格id
tag ---表格下的元素
maxJudgeCount ---判断超过多少个字数
showCount ---展示多少个字数
 */
function display(tableId,tag,maxJudgeCount,showCount){
    var elements=$("#"+tableId).find(tag);
    for (var i=0;i<elements.length;i++){
        $(elements[i]).attr("title",$(elements[i]).text());
        if ($(elements[i]).text().length>=maxJudgeCount){
            var str=$(elements[i]).text().substring(0,showCount)+"...";
            $(elements[i]).html(str);
        }
        //当鼠标在列表上悬停时，出现内容
        $(elements[i]).mouseover(function(){
            $(this).tooltip;
         });
    }
}

//搜索或者搜索分页后去根据select返回的value去确定第几个option被选中
/*
elements ---ex:select1 option,搜索框ID
value ---返回搜索框的值
 */
function get_option(elements,value){
   $(elements).each(function(index,element){
        if($(element).val()==value){
            $(element).attr("selected",true);
            //console.log($(element).val());
            return;
        }
    });
}

//根据返回值确认带模糊查询的搜索框
/*
elements ---搜索框divID
selectstep ---返回搜索框的值
startValue ---默认值
 */
function get_option_new_select(elements,selectstep,startValue){
    //带input的select
    if (selectstep==0){
        $(elements+" :button").attr("title",startValue);
        $(elements+" :button >span:nth-child(1)").text(startValue);
    }
    else{
        $(elements+" :button").attr("title",selectstep);
        $(elements+" :button >span:nth-child(1)").text(selectstep);
    }
}

//根据返回值确认带模糊查询的搜索框下拉框选择的位置
/*
elements ---搜索框divID
selectstep ---返回搜索框的值
 */

function choose_new_select(elements,selectstep){
    $(elements).find("ul").find("a").children("span:nth-child(1)").each(function(){
        if (selectstep==$(this).text()){
            //去除所有高亮
            $(elements).find("li").each(function(){
                $(this).attr("class","");
            });
            /*
            for (var i=0;i<lielsements.length;i++){
                lielsements[i].attr("class","");
            }*/
            //把匹配的高亮
            $(this).parent().parent().attr("class","selected");
            return false;
        }
    })
}

function openTab(url){
    if (url){
        //触发tab关闭
        $('span:contains("用例")').trigger('dblclick');
        //触发tab打开和跳转
        $("#step").find("a").attr("href-url",url);
        $("#step").trigger('click');
        $("#step").find("a").attr("href-url","/step/");
    }
}