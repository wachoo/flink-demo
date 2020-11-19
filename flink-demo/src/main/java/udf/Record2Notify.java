package udf;

import org.apache.hadoop.hive.ql.exec.UDF;
import org.json.JSONException;
import org.json.JSONObject;

/***
 * @Author wachoo
 * @Date 16:06 2020/11/19
 * @Desc //TODO
 **/
public class Record2Notify extends UDF {
    private static final String split_char = "!";
    private static final String null_char = "\002";

    public static String evaluate(int type, String line) throws JSONException {
        if (line == null) {
            return null;
        }
        JSONObject notify = new JSONObject();
        JSONObject entity = new JSONObject();
        notify.put("notifyType", type);
        String[] columns = line.split(split_char, -1);
        int size = columns.length / 2;
        for (int i = 0; i < size; i++) {
            String key = columns[i*2];
            String value = columns[i*2+1];
            if (isNull(key)) {
                throw new JSONException("Null key.1111111111");
            }
            if (!isNull(value)) {
                entity.put(key, value);
            }
        }
        notify.put("notifyEntity", entity);

        return notify.toString();
    }

    private static boolean isNull(String value) {
        return value == null || value.isEmpty() || value.equals(null_char);
    }

    public static void main(String[] args) throws JSONException {
        System.out.println(evaluate(13,"name!张三!age!13!school!小学"));
    }
}
