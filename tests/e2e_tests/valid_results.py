get_node_4string = {
  "id": "string4",
  "url": None,
  "date": "2024-11-02T05:25:26.896000",
  "parentId": None,
  "type": "FOLDER",
  "size": 6,
  "children": [
    {
      "id": "string2",
      "url": None,
      "date": "2024-11-02T05:25:26.896000",
      "parentId": "string4",
      "type": "FOLDER",
      "size": 6,
      "children": [
        {
          "id": "string",
          "url": "string",
          "date": "2024-11-02T04:25:26.896000",
          "parentId": "string2",
          "type": "FILE",
          "size": 6,
          "children": None
        }
      ]
    }
  ]
}

get_node_4string_final = {
  "id": "string4",
  "url": None,
  "date": "2024-11-02T06:25:26.896000",
  "parentId": None,
  "type": "FOLDER",
  "size": 16,
  "children": [
    {
      "id": "string2",
      "url": None,
      "date": "2024-11-02T05:25:26.896000",
      "parentId": "string4",
      "type": "FOLDER",
      "size": 6,
      "children": [
        {
          "id": "string",
          "url": "string",
          "date": "2024-11-02T04:25:26.896000",
          "parentId": "string2",
          "type": "FILE",
          "size": 6,
          "children": None
        }
      ]
    },
    {
      "id": "string3",
      "url": None,
      "date": "2024-11-02T06:25:26.896000",
      "parentId": "string4",
      "type": "FOLDER",
      "size": 0,
      "children": None
    },
    {
      "id": "string5",
      "url": "string1",
      "date": "2024-11-02T06:25:26.896000",
      "parentId": "string4",
      "type": "FILE",
      "size": 10,
      "children": None
    }
  ]
}

updates_no_deletes = {
  "items": [
    {
      "id": "string",
      "url": "string",
      "date": "2024-11-02T04:25:26.896000",
      "parentId": "string2",
      "type": "FILE",
      "size": 6
    },
    {
      "id": "string1",
      "url": "string1",
      "date": "2024-11-02T06:25:26.896000",
      "parentId": None,
      "type": "FILE",
      "size": 10
    },
    {
      "id": "string5",
      "url": "string1",
      "date": "2024-11-02T06:25:26.896000",
      "parentId": "string4",
      "type": "FILE",
      "size": 10
    }
  ]
}

get_string4_post_deletes = {
  "id": "string4",
  "url": None,
  "date": "2024-11-02T08:25:26.896000",
  "parentId": None,
  "type": "FOLDER",
  "size": 0,
  "children": [
    {
      "id": "string3",
      "url": None,
      "date": "2024-11-02T06:25:26.896000",
      "parentId": "string4",
      "type": "FOLDER",
      "size": 0,
      "children": None
    }
  ]
}

updates_post_deletes = {
  "items": [
    {
      "id": "string1",
      "url": "string1",
      "date": "2024-11-02T06:25:26.896000",
      "parentId": None,
      "type": "FILE",
      "size": 10
    }
  ]
}

string4_history = {
  "items": [
    {
      "id": "string4",
      "url": None,
      "date": "2024-11-02T05:25:26.896000",
      "parentId": None,
      "type": "FOLDER",
      "size": 6
    },
    {
      "id": "string4",
      "url": None,
      "date": "2024-11-02T06:25:26.896000",
      "parentId": None,
      "type": "FOLDER",
      "size": 16
    },
    {
      "id": "string4",
      "url": None,
      "date": "2024-11-02T07:25:26.896000",
      "parentId": None,
      "type": "FOLDER",
      "size": 10
    },
    {
      "id": "string4",
      "url": None,
      "date": "2024-11-02T08:25:26.896000",
      "parentId": None,
      "type": "FOLDER",
      "size": 0
    }
  ]
}