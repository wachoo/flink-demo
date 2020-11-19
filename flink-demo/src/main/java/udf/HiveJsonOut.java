package udf;

import org.apache.hadoop.hive.ql.exec.UDF;
import org.json.JSONException;
import org.json.JSONObject;

/***
 * @Author wachoo
 * @Date 15:59 2020/11/19
 * @Desc //TODO
 **/
public class HiveJsonOut extends UDF {

    public static String evaluate(String jsonStr) throws JSONException {
        String[] split = jsonStr.split(",");
        JSONObject result = new JSONObject();
        result.put("key", split[0]);
        result.put("value", split[1]);
        return String.valueOf(result);
    }
}
