def get_file_as_string(filename)
  data = ''
  begin
    f = File.open(filename, "r") 
    f.each_line do |line|
      data += line
    end
  rescue SystemCallError
      data = 'Could not find file: ' + filename
  end
  return data
end


class TaskLog < ActiveRecord::Base
	belongs_to :task
	belongs_to :cattle

	def stdout
	  filepath = self[:stdout]
	  return get_file_as_string(filepath)
	end

	def stderr
	  filepath = self[:stderr]
	  return get_file_as_string(filepath)
	end
end
