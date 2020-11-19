package udf;

import org.apache.hadoop.hive.ql.exec.UDF;
import org.json.JSONException;
import org.json.JSONArray;

/***
 * @Author wachoo
 * @Date 16:07 2020/11/19
 * @Desc //TODO
 **/
public class HiveJson extends UDF{

    public static JSONArray evaluate(String jsonStr) throws JSONException {
        String[] split = jsonStr.split("!!");
        JSONArray jsonArray = new JSONArray();
        jsonArray.put(split[0]);
        jsonArray.put(split[1]);
        jsonArray.put(split[2]);
        jsonArray.put(split[3]);
        return jsonArray;
    }

}
